#!/usr/bin/env python3
"""
License Policy Compliance Checker
Compares detected licenses against company policy database
"""

import yaml
import json
import argparse
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from pathlib import Path


class PolicyStatus(Enum):
    """License policy compliance status"""
    APPROVED = "approved"
    CONDITIONAL = "conditional"
    FORBIDDEN = "forbidden"
    UNKNOWN = "unknown"
    INCOMPATIBLE = "incompatible"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PolicyCheckResult:
    """Result of a policy check for a single package"""
    package_id: str
    package_name: str
    package_version: str
    package_type: str

    detected_license: str
    normalized_license: str

    policy_status: str
    risk_level: str
    category: str

    auto_approve: bool
    approval_required: bool
    approvers: List[str]

    conditions: List[str]
    reason: str
    action: str

    compatibility_issues: List[Dict]
    alternative_needed: bool

    def to_dict(self):
        return asdict(self)


class LicensePolicyChecker:
    """Main policy checker class"""

    def __init__(self, policy_file: str):
        """Initialize with policy configuration"""
        self.policy_file = policy_file
        self.policy = self._load_policy()

        # Build lookup tables for fast checking
        self.approved_licenses = self._build_approved_list()
        self.conditional_licenses = self._build_conditional_list()
        self.forbidden_licenses = self._build_forbidden_list()

    def _load_policy(self) -> Dict:
        """Load policy from YAML file"""
        try:
            with open(self.policy_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data['company_license_policy']
        except FileNotFoundError:
            print(f"❌ Policy file not found: {self.policy_file}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"❌ Error parsing policy file: {e}")
            sys.exit(1)

    def _build_approved_list(self) -> Dict[str, Dict]:
        """Build flat list of approved licenses with metadata"""
        approved = {}
        for category, data in self.policy['approved_licenses'].items():
            for license_id in data['licenses']:
                approved[license_id] = {
                    'category': category,
                    'risk_level': data.get('risk_level', 'low'),
                    'auto_approve': data.get('auto_approve', True),
                    'conditions': data.get('conditions', []),
                    'description': data.get('description', '')
                }
        return approved

    def _build_conditional_list(self) -> Dict[str, Dict]:
        """Build flat list of conditional licenses"""
        conditional = {}
        for category, data in self.policy['conditional_licenses'].items():
            for license_id in data['licenses']:
                conditional[license_id] = {
                    'category': category,
                    'risk_level': data.get('risk_level', 'medium'),
                    'auto_approve': data.get('auto_approve', False),
                    'approval_required': data.get('approval_required', True),
                    'approvers': data.get('approvers', []),
                    'conditions': data.get('conditions', []),
                    'description': data.get('description', ''),
                    'use_cases': data.get('use_cases', {})
                }
        return conditional

    def _build_forbidden_list(self) -> Dict[str, Dict]:
        """Build flat list of forbidden licenses"""
        forbidden = {}
        for category, data in self.policy['forbidden_licenses'].items():
            for license_id in data['licenses']:
                forbidden[license_id] = {
                    'category': category,
                    'reason': data.get('reason', ''),
                    'risk_level': data.get('risk_level', 'critical'),
                    'action': data.get('action', 'reject')
                }
        return forbidden

    def normalize_license(self, license_str: str) -> str:
        """
        Normalize license string for comparison
        Handles variations in license naming
        """
        if not license_str:
            return "NOASSERTION"

        # Remove whitespace
        normalized = license_str.strip()

        # Handle common variations
        mappings = {
            'MIT License': 'MIT',
            'Apache License 2.0': 'Apache-2.0',
            'BSD License': 'BSD-3-Clause',
            'GNU General Public License v3 or later (GPLv3+)': 'GPL-3.0-or-later',
            'GNU General Public License v3.0': 'GPL-3.0-only',
            'NONE': 'NOASSERTION',
            '': 'NOASSERTION'
        }

        return mappings.get(normalized, normalized)

    def check_license(self, license_expression: str) -> Tuple[PolicyStatus, Dict]:
        """
        Check if license is approved, conditional, forbidden, or unknown

        Args:
            license_expression: SPDX license expression (e.g., "MIT", "MIT OR Apache-2.0")

        Returns:
            Tuple of (PolicyStatus, metadata dict)
        """
        normalized = self.normalize_license(license_expression)

        # Handle SPDX expressions with OR operator (dual licensing)
        if ' OR ' in normalized:
            return self._check_dual_license(normalized)

        # Handle SPDX expressions with AND operator (multi-licensing)
        if ' AND ' in normalized:
            return self._check_multi_license(normalized)

        # Single license check
        if normalized in self.approved_licenses:
            return PolicyStatus.APPROVED, self.approved_licenses[normalized]

        if normalized in self.conditional_licenses:
            return PolicyStatus.CONDITIONAL, self.conditional_licenses[normalized]

        if normalized in self.forbidden_licenses:
            return PolicyStatus.FORBIDDEN, self.forbidden_licenses[normalized]

        # Unknown license
        return PolicyStatus.UNKNOWN, {
            'category': 'unknown',
            'risk_level': 'high',
            'action': self.policy['special_rules']['unknown_license_action'],
            'reason': 'License not found in policy database'
        }

    def _check_dual_license(self, license_expr: str) -> Tuple[PolicyStatus, Dict]:
        """
        Handle dual-licensed packages (OR operator)
        Strategy from policy: choose_most_permissive
        """
        licenses = [l.strip() for l in license_expr.split(' OR ')]

        # Check each option
        results = []
        for lic in licenses:
            status, metadata = self.check_license(lic)
            results.append((lic, status, metadata))

        # Apply strategy: choose_most_permissive
        strategy = self.policy['special_rules']['dual_license_strategy']

        if strategy == 'choose_most_permissive':
            # Prefer approved licenses
            for lic, status, metadata in results:
                if status == PolicyStatus.APPROVED:
                    metadata['dual_license_choice'] = lic
                    metadata['dual_license_options'] = licenses
                    return PolicyStatus.APPROVED, metadata

            # Fall back to conditional
            for lic, status, metadata in results:
                if status == PolicyStatus.CONDITIONAL:
                    metadata['dual_license_choice'] = lic
                    metadata['dual_license_options'] = licenses
                    return PolicyStatus.CONDITIONAL, metadata

        # If all forbidden or unknown
        return PolicyStatus.FORBIDDEN, {
            'category': 'dual_licensed',
            'risk_level': 'high',
            'reason': f'All license options are forbidden or unknown: {licenses}',
            'dual_license_options': licenses
        }

    def _check_multi_license(self, license_expr: str) -> Tuple[PolicyStatus, Dict]:
        """
        Handle multi-licensed packages (AND operator)
        ALL licenses must be compatible
        """
        licenses = [l.strip() for l in license_expr.split(' AND ')]

        # Check compatibility
        compatibility_issues = []
        for i, lic1 in enumerate(licenses):
            for lic2 in licenses[i+1:]:
                is_compatible, reason = self._check_compatibility(lic1, lic2)
                if not is_compatible:
                    compatibility_issues.append({
                        'license1': lic1,
                        'license2': lic2,
                        'reason': reason
                    })

        if compatibility_issues:
            return PolicyStatus.INCOMPATIBLE, {
                'category': 'multi_licensed_incompatible',
                'risk_level': 'critical',
                'reason': 'License combination has compatibility issues',
                'compatibility_issues': compatibility_issues,
                'licenses': licenses
            }

        # All must be approved or conditional
        statuses = []
        for lic in licenses:
            status, metadata = self.check_license(lic)
            statuses.append((lic, status, metadata))

        # If any is forbidden, entire combination is forbidden
        if any(status == PolicyStatus.FORBIDDEN for _, status, _ in statuses):
            return PolicyStatus.FORBIDDEN, {
                'category': 'multi_licensed_forbidden',
                'risk_level': 'critical',
                'reason': 'At least one license in combination is forbidden',
                'licenses': licenses
            }

        # If all approved, combination is approved
        if all(status == PolicyStatus.APPROVED for _, status, _ in statuses):
            return PolicyStatus.APPROVED, {
                'category': 'multi_licensed_approved',
                'risk_level': 'low',
                'licenses': licenses,
                'conditions': []
            }

        # Otherwise, manual review needed
        return PolicyStatus.CONDITIONAL, {
            'category': 'multi_licensed_conditional',
            'risk_level': 'medium',
            'reason': 'Multi-license combination requires review',
            'licenses': licenses,
            'approval_required': True
        }

    def _check_compatibility(self, lic1: str, lic2: str) -> Tuple[bool, str]:
        """Check if two licenses are compatible"""
        compatibility_matrix = self.policy.get('license_compatibility', [])

        # Check both orderings
        for combo in compatibility_matrix:
            combo_str = combo['combination']
            if (f"{lic1} AND {lic2}" == combo_str or
                f"{lic2} AND {lic1}" == combo_str):
                return combo['compatible'], combo.get('reason', '')

        # Default: assume compatible if not explicitly listed as incompatible
        return True, "Not explicitly listed as incompatible"

    def check_package(self, package_data: Dict) -> PolicyCheckResult:
        """
        Check a single package against policy

        Args:
            package_data: Dict with keys: id, name, version, type, license

        Returns:
            PolicyCheckResult object
        """
        pkg_id = package_data.get('id', 'unknown')
        pkg_name = package_data.get('name', 'unknown')
        pkg_version = package_data.get('version', 'unknown')
        pkg_type = package_data.get('type', 'unknown')
        detected_license = package_data.get('license', 'NOASSERTION')

        # Normalize and check
        normalized_license = self.normalize_license(detected_license)
        status, metadata = self.check_license(normalized_license)

        # Build result
        result = PolicyCheckResult(
            package_id=pkg_id,
            package_name=pkg_name,
            package_version=pkg_version,
            package_type=pkg_type,
            detected_license=detected_license,
            normalized_license=normalized_license,
            policy_status=status.value,
            risk_level=metadata.get('risk_level', 'unknown'),
            category=metadata.get('category', 'unknown'),
            auto_approve=metadata.get('auto_approve', False),
            approval_required=metadata.get('approval_required', False),
            approvers=metadata.get('approvers', []),
            conditions=metadata.get('conditions', []),
            reason=metadata.get('reason', ''),
            action=metadata.get('action', 'review'),
            compatibility_issues=metadata.get('compatibility_issues', []),
            alternative_needed=(status == PolicyStatus.FORBIDDEN)
        )

        return result

    def check_ort_results(self, ort_result_file: str) -> List[PolicyCheckResult]:
        """
        Check all packages in ORT analyzer result file

        Args:
            ort_result_file: Path to ORT analyzer-result.yml

        Returns:
            List of PolicyCheckResult objects
        """
        try:
            with open(ort_result_file, 'r', encoding='utf-8') as f:
                ort_data = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ ORT result file not found: {ort_result_file}")
            sys.exit(1)

        results = []
        packages = ort_data.get('analyzer', {}).get('result', {}).get('packages', [])

        for pkg in packages:
            pkg_id = pkg.get('id', '')

            # Extract package details
            # Format: "PyPI::package:version" or "NPM::package:version"
            parts = pkg_id.split(':')
            pkg_type = parts[0] if len(parts) > 0 else 'unknown'
            pkg_name = parts[2] if len(parts) > 2 else 'unknown'
            pkg_version = parts[3] if len(parts) > 3 else 'unknown'

            # Get declared license
            declared_license = pkg.get('declared_licenses_processed', {}).get('spdx_expression', 'NOASSERTION')
            if declared_license == 'NOASSERTION' or not declared_license:
                # Fallback to declared_licenses list
                declared_list = pkg.get('declared_licenses', [])
                declared_license = ', '.join(declared_list) if declared_list else 'NOASSERTION'

            package_data = {
                'id': pkg_id,
                'name': pkg_name,
                'version': pkg_version,
                'type': pkg_type,
                'license': declared_license
            }

            result = self.check_package(package_data)
            results.append(result)

        return results

    def generate_summary_stats(self, results: List[PolicyCheckResult]) -> Dict:
        """Generate summary statistics"""
        total = len(results)
        approved = sum(1 for r in results if r.policy_status == 'approved')
        conditional = sum(1 for r in results if r.policy_status == 'conditional')
        forbidden = sum(1 for r in results if r.policy_status == 'forbidden')
        unknown = sum(1 for r in results if r.policy_status == 'unknown')
        incompatible = sum(1 for r in results if r.policy_status == 'incompatible')

        # Risk breakdown
        critical = sum(1 for r in results if r.risk_level == 'critical')
        high = sum(1 for r in results if r.risk_level == 'high')
        medium = sum(1 for r in results if r.risk_level == 'medium')
        low = sum(1 for r in results if r.risk_level == 'low')

        # Calculate compliance score (0-100)
        if total > 0:
            compliance_score = int((approved / total) * 100)
        else:
            compliance_score = 0

        return {
            'total_packages': total,
            'approved': approved,
            'conditional': conditional,
            'forbidden': forbidden,
            'unknown': unknown,
            'incompatible': incompatible,
            'risk_critical': critical,
            'risk_high': high,
            'risk_medium': medium,
            'risk_low': low,
            'compliance_score': compliance_score,
            'scan_date': datetime.now().isoformat()
        }

    def generate_html_report(self, results: List[PolicyCheckResult], output_file: str):
        """Generate beautiful HTML compliance report"""
        stats = self.generate_summary_stats(results)

        # Sort results by risk level
        sorted_results = sorted(results, key=lambda r: {
            'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'unknown': 4
        }.get(r.risk_level, 5))

        html_content = self._build_html_report(stats, sorted_results)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ HTML report generated: {output_file}")

    def _build_html_report(self, stats: Dict, results: List[PolicyCheckResult]) -> str:
        """Build HTML report content"""

        # Status colors
        status_colors = {
            'approved': '#28a745',
            'conditional': '#ffc107',
            'forbidden': '#dc3545',
            'unknown': '#6c757d',
            'incompatible': '#e74c3c'
        }

        # Build package rows
        package_rows = ""
        for r in results:
            status_color = status_colors.get(r.policy_status, '#6c757d')

            # Conditions HTML
            conditions_html = ""
            if r.conditions:
                conditions_html = "<ul class='conditions-list'>"
                for cond in r.conditions:
                    conditions_html += f"<li>{cond}</li>"
                conditions_html += "</ul>"

            # Approvers HTML
            approvers_html = ""
            if r.approvers:
                approvers_html = f"<div class='approvers'>Approvers: {', '.join(r.approvers)}</div>"

            # Alternative needed badge
            alt_badge = ""
            if r.alternative_needed:
                alt_badge = "<span class='badge badge-danger'>Alternative Needed</span>"

            package_rows += f"""
            <tr class="risk-{r.risk_level}">
                <td><code>{r.package_name}</code></td>
                <td>{r.package_version}</td>
                <td><span class="badge badge-secondary">{r.package_type}</span></td>
                <td><code>{r.detected_license}</code></td>
                <td>
                    <span class="badge" style="background-color: {status_color};">
                        {r.policy_status.upper()}
                    </span>
                    {alt_badge}
                </td>
                <td>
                    <span class="badge badge-risk-{r.risk_level}">
                        {r.risk_level.upper()}
                    </span>
                </td>
                <td>
                    {r.reason}
                    {conditions_html}
                    {approvers_html}
                </td>
            </tr>
            """

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>License Policy Compliance Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}

        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}

        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}

        .stat-card .label {{
            color: #6c757d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .stat-card.approved .number {{ color: #28a745; }}
        .stat-card.conditional .number {{ color: #ffc107; }}
        .stat-card.forbidden .number {{ color: #dc3545; }}
        .stat-card.unknown .number {{ color: #6c757d; }}
        .stat-card.score .number {{ color: #667eea; }}

        .compliance-score {{
            padding: 40px;
            text-align: center;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }}

        .score-circle {{
            width: 200px;
            height: 200px;
            margin: 0 auto;
            border-radius: 50%;
            background: conic-gradient(
                #28a745 0deg {stats['compliance_score'] * 3.6}deg,
                #e9ecef {stats['compliance_score'] * 3.6}deg 360deg
            );
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }}

        .score-circle::before {{
            content: "{stats['compliance_score']}%";
            position: absolute;
            width: 160px;
            height: 160px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
        }}

        .content {{
            padding: 40px;
        }}

        .section-title {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
        }}

        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            color: white;
            margin: 2px;
        }}

        .badge-secondary {{ background: #6c757d; }}
        .badge-danger {{ background: #dc3545; }}

        .badge-risk-critical {{ background: #dc3545; }}
        .badge-risk-high {{ background: #fd7e14; }}
        .badge-risk-medium {{ background: #ffc107; color: #333; }}
        .badge-risk-low {{ background: #28a745; }}

        .risk-critical {{ background: #ffebee; }}
        .risk-high {{ background: #fff3e0; }}
        .risk-medium {{ background: #fffde7; }}
        .risk-low {{ background: #f1f8f4; }}

        .conditions-list {{
            margin: 10px 0 0 20px;
            font-size: 0.9em;
            color: #666;
        }}

        .approvers {{
            margin-top: 8px;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 4px;
            font-size: 0.9em;
            color: #495057;
        }}

        code {{
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}

        .footer {{
            padding: 30px;
            text-align: center;
            background: #f8f9fa;
            color: #6c757d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 License Policy Compliance Report</h1>
            <p>Scan Date: {stats['scan_date']}</p>
            <p>Company: {self.policy.get('company_name', 'Your Company')}</p>
        </div>

        <div class="stats">
            <div class="stat-card approved">
                <div class="number">{stats['approved']}</div>
                <div class="label">Approved</div>
            </div>
            <div class="stat-card conditional">
                <div class="number">{stats['conditional']}</div>
                <div class="label">Conditional</div>
            </div>
            <div class="stat-card forbidden">
                <div class="number">{stats['forbidden']}</div>
                <div class="label">Forbidden</div>
            </div>
            <div class="stat-card unknown">
                <div class="number">{stats['unknown']}</div>
                <div class="label">Unknown</div>
            </div>
            <div class="stat-card">
                <div class="number">{stats['risk_critical']}</div>
                <div class="label">Critical Risk</div>
            </div>
        </div>

        <div class="compliance-score">
            <h2 style="margin-bottom: 20px; color: #667eea;">Compliance Score</h2>
            <div class="score-circle"></div>
            <p style="margin-top: 20px; color: #6c757d;">
                {stats['approved']} out of {stats['total_packages']} packages approved
            </p>
        </div>

        <div class="content">
            <h2 class="section-title">📦 Package Details</h2>

            <table>
                <thead>
                    <tr>
                        <th>Package</th>
                        <th>Version</th>
                        <th>Type</th>
                        <th>License</th>
                        <th>Status</th>
                        <th>Risk</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    {package_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>Generated by Advanced License Curation Workflow</p>
            <p>Policy Version: {self.policy.get('policy_version', '1.0.0')}</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def export_json(self, results: List[PolicyCheckResult], output_file: str):
        """Export results to JSON"""
        stats = self.generate_summary_stats(results)

        data = {
            'summary': stats,
            'packages': [r.to_dict() for r in results]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f"✅ JSON export saved: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='License Policy Compliance Checker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check ORT results against policy
  python policy_checker.py \\
    --policy config/company-policy.yml \\
    --ort-results ort-results/analyzer/analyzer-result.yml \\
    --output policy-compliance-report.html

  # Export to JSON
  python policy_checker.py \\
    --policy config/company-policy.yml \\
    --ort-results ort-results/analyzer/analyzer-result.yml \\
    --json policy-results.json
        """
    )

    parser.add_argument(
        '--policy',
        required=True,
        help='Path to company policy YAML file'
    )

    parser.add_argument(
        '--ort-results',
        required=True,
        help='Path to ORT analyzer-result.yml file'
    )

    parser.add_argument(
        '--output',
        default='policy-compliance-report.html',
        help='Output HTML report file (default: policy-compliance-report.html)'
    )

    parser.add_argument(
        '--json',
        help='Export results to JSON file'
    )

    args = parser.parse_args()

    print("🔍 License Policy Compliance Checker")
    print("=" * 60)

    # Initialize checker
    print(f"📁 Loading policy: {args.policy}")
    checker = LicensePolicyChecker(args.policy)
    print(f"✅ Policy loaded: {checker.policy['company_name']}")
    print(f"   Version: {checker.policy['policy_version']}")
    print()

    # Check packages
    print(f"📦 Analyzing packages from: {args.ort_results}")
    results = checker.check_ort_results(args.ort_results)
    print(f"✅ Analyzed {len(results)} packages")
    print()

    # Generate summary
    stats = checker.generate_summary_stats(results)
    print("📊 Summary:")
    print(f"   ✅ Approved:    {stats['approved']}")
    print(f"   ⚠️  Conditional: {stats['conditional']}")
    print(f"   ❌ Forbidden:   {stats['forbidden']}")
    print(f"   ❓ Unknown:     {stats['unknown']}")
    print(f"   🚫 Incompatible: {stats['incompatible']}")
    print(f"   📈 Compliance Score: {stats['compliance_score']}%")
    print()

    # Generate HTML report
    print(f"📄 Generating HTML report: {args.output}")
    checker.generate_html_report(results, args.output)

    # Export JSON if requested
    if args.json:
        print(f"💾 Exporting to JSON: {args.json}")
        checker.export_json(results, args.json)

    print()
    print("=" * 60)
    print("✅ Policy check complete!")

    # Exit with error code if forbidden or critical packages found
    if stats['forbidden'] > 0 or stats['risk_critical'] > 0:
        print("⚠️  WARNING: Forbidden or critical risk packages detected!")
        sys.exit(1)


if __name__ == '__main__':
    main()
