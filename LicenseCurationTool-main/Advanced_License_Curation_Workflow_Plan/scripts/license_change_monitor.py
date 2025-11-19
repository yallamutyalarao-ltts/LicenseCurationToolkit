#!/usr/bin/env python3
"""
License Change Monitor
Detects when package licenses suddenly change between scans
Maintains historical tracking database
"""

import json
import yaml
import argparse
import hashlib
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


class ChangeSeverity:
    """License change severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class LicenseChange:
    """Represents a detected license change"""
    package_id: str
    package_name: str
    package_version: str

    previous_license: str
    current_license: str

    change_date: str
    first_seen_date: str

    severity: str
    risk_assessment: str
    requires_action: bool

    reason: str
    recommended_actions: List[str]

    def to_dict(self):
        return asdict(self)


class LicenseChangeMonitor:
    """Monitor and track license changes over time"""

    def __init__(self, history_file: str = '.ort/license-history.json',
                 policy_file: Optional[str] = None):
        """
        Initialize monitor

        Args:
            history_file: Path to license history database
            policy_file: Optional policy file for severity assessment
        """
        self.history_file = history_file
        self.history = self._load_history()

        self.policy = None
        if policy_file:
            with open(policy_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.policy = data['company_license_policy']

    def _load_history(self) -> Dict:
        """Load license history from file"""
        if Path(self.history_file).exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading history file: {e}")
                return self._create_empty_history()
        else:
            return self._create_empty_history()

    def _create_empty_history(self) -> Dict:
        """Create empty history structure"""
        return {
            'tracking_started': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'total_scans': 0,
            'packages': {}
        }

    def _save_history(self):
        """Save history to file"""
        self.history['last_updated'] = datetime.now().isoformat()

        # Ensure directory exists
        Path(self.history_file).parent.mkdir(parents=True, exist_ok=True)

        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2)

        print(f"✅ History saved to: {self.history_file}")

    def initialize_tracking(self, ort_result_file: str):
        """Initialize tracking with first scan"""
        print("🔧 Initializing license tracking...")

        packages = self._parse_ort_results(ort_result_file)

        for pkg_id, pkg_data in packages.items():
            self.history['packages'][pkg_id] = {
                'package_name': pkg_data['name'],
                'package_type': pkg_data['type'],
                'first_seen': datetime.now().isoformat(),
                'current_license': pkg_data['license'],
                'current_version': pkg_data['version'],
                'license_history': [
                    {
                        'date': datetime.now().isoformat(),
                        'license': pkg_data['license'],
                        'version': pkg_data['version'],
                        'source': 'ORT',
                        'hash': self._compute_hash(pkg_data)
                    }
                ],
                'change_count': 0,
                'last_verified': datetime.now().isoformat()
            }

        self.history['total_scans'] = 1
        self._save_history()

        print(f"✅ Initialized tracking for {len(packages)} packages")

    def check_for_changes(self, ort_result_file: str) -> List[LicenseChange]:
        """
        Check for license changes since last scan

        Args:
            ort_result_file: Path to ORT analyzer-result.yml

        Returns:
            List of LicenseChange objects
        """
        print("🔍 Checking for license changes...")

        changes_detected = []
        packages = self._parse_ort_results(ort_result_file)

        for pkg_id, pkg_data in packages.items():
            current_license = pkg_data['license']
            current_version = pkg_data['version']

            if pkg_id in self.history['packages']:
                # Package exists in history
                pkg_history = self.history['packages'][pkg_id]
                previous_license = pkg_history['current_license']
                previous_version = pkg_history['current_version']

                # Check if license changed
                if current_license != previous_license:
                    # License changed!
                    change = self._create_license_change(
                        pkg_id=pkg_id,
                        pkg_data=pkg_data,
                        previous_license=previous_license,
                        current_license=current_license,
                        first_seen=pkg_history['first_seen']
                    )

                    changes_detected.append(change)

                    # Update history
                    pkg_history['license_history'].append({
                        'date': datetime.now().isoformat(),
                        'license': current_license,
                        'version': current_version,
                        'source': 'ORT',
                        'hash': self._compute_hash(pkg_data),
                        'change_detected': True
                    })

                    pkg_history['current_license'] = current_license
                    pkg_history['current_version'] = current_version
                    pkg_history['change_count'] += 1

                else:
                    # No change, update last verified
                    pkg_history['last_verified'] = datetime.now().isoformat()

            else:
                # New package
                self.history['packages'][pkg_id] = {
                    'package_name': pkg_data['name'],
                    'package_type': pkg_data['type'],
                    'first_seen': datetime.now().isoformat(),
                    'current_license': current_license,
                    'current_version': current_version,
                    'license_history': [
                        {
                            'date': datetime.now().isoformat(),
                            'license': current_license,
                            'version': current_version,
                            'source': 'ORT',
                            'hash': self._compute_hash(pkg_data)
                        }
                    ],
                    'change_count': 0,
                    'last_verified': datetime.now().isoformat()
                }

        # Increment scan count
        self.history['total_scans'] = self.history.get('total_scans', 0) + 1

        # Save updated history
        self._save_history()

        return changes_detected

    def _parse_ort_results(self, ort_result_file: str) -> Dict[str, Dict]:
        """Parse ORT results and extract package license info"""
        try:
            with open(ort_result_file, 'r', encoding='utf-8') as f:
                ort_data = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ ORT result file not found: {ort_result_file}")
            sys.exit(1)

        packages = {}
        ort_packages = ort_data.get('analyzer', {}).get('result', {}).get('packages', [])

        for pkg in ort_packages:
            pkg_id = pkg.get('id', '')

            # Parse package ID
            parts = pkg_id.split(':')
            pkg_type = parts[0] if len(parts) > 0 else 'unknown'
            pkg_name = parts[2] if len(parts) > 2 else 'unknown'
            pkg_version = parts[3] if len(parts) > 3 else 'unknown'

            # Get license
            declared_license = pkg.get('declared_licenses_processed', {}).get(
                'spdx_expression', 'NOASSERTION'
            )
            if not declared_license or declared_license == 'NOASSERTION':
                declared_list = pkg.get('declared_licenses', [])
                declared_license = ', '.join(declared_list) if declared_list else 'NOASSERTION'

            packages[pkg_id] = {
                'name': pkg_name,
                'type': pkg_type,
                'version': pkg_version,
                'license': declared_license
            }

        return packages

    def _compute_hash(self, pkg_data: Dict) -> str:
        """Compute hash of package data for change detection"""
        data_str = f"{pkg_data['name']}:{pkg_data['version']}:{pkg_data['license']}"
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    def _create_license_change(self,
                               pkg_id: str,
                               pkg_data: Dict,
                               previous_license: str,
                               current_license: str,
                               first_seen: str) -> LicenseChange:
        """Create LicenseChange object with severity assessment"""

        # Assess severity
        severity = self._assess_change_severity(previous_license, current_license)

        # Determine if action required
        requires_action = severity in [ChangeSeverity.CRITICAL, ChangeSeverity.HIGH]

        # Risk assessment
        risk_assessment = self._assess_risk(previous_license, current_license, severity)

        # Generate reason
        reason = self._generate_change_reason(previous_license, current_license, severity)

        # Recommended actions
        recommended_actions = self._generate_recommendations(
            pkg_data, previous_license, current_license, severity
        )

        return LicenseChange(
            package_id=pkg_id,
            package_name=pkg_data['name'],
            package_version=pkg_data['version'],
            previous_license=previous_license,
            current_license=current_license,
            change_date=datetime.now().isoformat(),
            first_seen_date=first_seen,
            severity=severity,
            risk_assessment=risk_assessment,
            requires_action=requires_action,
            reason=reason,
            recommended_actions=recommended_actions
        )

    def _assess_change_severity(self, old_license: str, new_license: str) -> str:
        """Assess severity of license change"""

        # License categories
        permissive = ['MIT', 'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'ISC']
        weak_copyleft = ['LGPL-2.1', 'LGPL-3.0', 'MPL-2.0']
        strong_copyleft = ['GPL-2.0', 'GPL-3.0', 'AGPL-3.0']

        # Use policy if available
        if self.policy:
            severity_config = self.policy.get('special_rules', {}).get(
                'license_change_severity', {}
            )

            # Permissive to copyleft
            if old_license in permissive and new_license in strong_copyleft:
                return severity_config.get('permissive_to_copyleft', ChangeSeverity.CRITICAL)

            # Copyleft to permissive (unusual, verify!)
            if old_license in strong_copyleft and new_license in permissive:
                return severity_config.get('copyleft_to_permissive', ChangeSeverity.HIGH)

            # Permissive to permissive
            if old_license in permissive and new_license in permissive:
                return severity_config.get('permissive_to_permissive', ChangeSeverity.LOW)

        # Default assessment
        if old_license in permissive and new_license in strong_copyleft:
            return ChangeSeverity.CRITICAL

        if old_license in strong_copyleft and new_license in permissive:
            return ChangeSeverity.HIGH

        if old_license in permissive and new_license in permissive:
            return ChangeSeverity.LOW

        return ChangeSeverity.MEDIUM

    def _assess_risk(self, old_license: str, new_license: str, severity: str) -> str:
        """Generate risk assessment text"""
        if severity == ChangeSeverity.CRITICAL:
            return ("Critical risk: License became more restrictive (copyleft). "
                   "May require open-sourcing derivative works.")

        if severity == ChangeSeverity.HIGH:
            return ("High risk: Unusual license change. Verify package maintainer "
                   "intent and check for potential security issues.")

        if severity == ChangeSeverity.MEDIUM:
            return "Medium risk: License family changed. Review new license terms."

        return "Low risk: Minor license change within same category."

    def _generate_change_reason(self, old_license: str, new_license: str, severity: str) -> str:
        """Generate human-readable reason for change"""
        return (f"License changed from '{old_license}' to '{new_license}'. "
               f"Severity: {severity.upper()}")

    def _generate_recommendations(self,
                                 pkg_data: Dict,
                                 old_license: str,
                                 new_license: str,
                                 severity: str) -> List[str]:
        """Generate recommended actions based on change"""
        actions = []

        if severity == ChangeSeverity.CRITICAL:
            actions.append("⛔ IMMEDIATE ACTION REQUIRED")
            actions.append("1. Stop using this package version immediately")
            actions.append("2. Review legal implications with compliance team")
            actions.append("3. Consider reverting to previous version or finding alternative")
            actions.append("4. Update package dependencies to pin to safe version")

        elif severity == ChangeSeverity.HIGH:
            actions.append("⚠️ URGENT REVIEW REQUIRED")
            actions.append("1. Verify license change is legitimate (not typo or error)")
            actions.append("2. Check package maintainer communications")
            actions.append("3. Review new license terms for compatibility")
            actions.append("4. Consider alternative packages")

        elif severity == ChangeSeverity.MEDIUM:
            actions.append("📋 REVIEW RECOMMENDED")
            actions.append("1. Review new license terms")
            actions.append("2. Verify compatibility with company policy")
            actions.append("3. Update internal documentation")

        else:
            actions.append("ℹ️ AWARENESS ONLY")
            actions.append("1. Note the change in documentation")
            actions.append("2. Verify no compliance issues")

        # Add verification steps
        actions.append(f"5. Verify from package registry: https://pypi.org/project/{pkg_data['name']}/")
        actions.append(f"6. Check GitHub repository for LICENSE file changes")

        return actions

    def generate_html_report(self, changes: List[LicenseChange], output_file: str):
        """Generate HTML report for license changes"""

        if not changes:
            print("✅ No license changes detected")
            return

        # Sort by severity
        severity_order = {
            ChangeSeverity.CRITICAL: 0,
            ChangeSeverity.HIGH: 1,
            ChangeSeverity.MEDIUM: 2,
            ChangeSeverity.LOW: 3
        }
        sorted_changes = sorted(changes, key=lambda x: severity_order.get(x.severity, 4))

        # Build change rows
        change_rows = ""
        for change in sorted_changes:
            severity_class = f"severity-{change.severity}"
            severity_icon = self._get_severity_icon(change.severity)

            actions_html = "<ol class='actions-list'>"
            for action in change.recommended_actions:
                actions_html += f"<li>{action}</li>"
            actions_html += "</ol>"

            change_rows += f"""
            <tr class="{severity_class}">
                <td>
                    <span class="severity-badge {severity_class}">
                        {severity_icon} {change.severity.upper()}
                    </span>
                </td>
                <td>
                    <strong>{change.package_name}</strong>
                    <div class="version">v{change.package_version}</div>
                </td>
                <td class="license-change">
                    <div class="old-license">{change.previous_license}</div>
                    <div class="arrow">↓</div>
                    <div class="new-license">{change.current_license}</div>
                </td>
                <td>{change.change_date[:10]}</td>
                <td class="risk-cell">{change.risk_assessment}</td>
                <td class="actions-cell">
                    {actions_html}
                </td>
            </tr>
            """

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>License Change Alert Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            padding: 20px;
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
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .alert-box {{
            background: rgba(255,255,255,0.2);
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}

        .alert-box h2 {{
            font-size: 1.5em;
            margin-bottom: 10px;
        }}

        .content {{
            padding: 40px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        th {{
            background: #ff6b6b;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}

        td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
            vertical-align: top;
        }}

        .severity-critical {{ background: #ffebee; }}
        .severity-high {{ background: #fff3e0; }}
        .severity-medium {{ background: #fffde7; }}
        .severity-low {{ background: #f1f8f4; }}

        .severity-badge {{
            display: inline-block;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
            color: white;
        }}

        .severity-badge.severity-critical {{ background: #d32f2f; }}
        .severity-badge.severity-high {{ background: #f57c00; }}
        .severity-badge.severity-medium {{ background: #fbc02d; color: #333; }}
        .severity-badge.severity-low {{ background: #388e3c; }}

        .version {{
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 5px;
        }}

        .license-change {{
            text-align: center;
        }}

        .old-license {{
            padding: 8px;
            background: #ffebee;
            border-radius: 4px;
            margin-bottom: 5px;
            font-family: monospace;
        }}

        .arrow {{
            font-size: 1.5em;
            color: #ff6b6b;
            margin: 5px 0;
        }}

        .new-license {{
            padding: 8px;
            background: #e8f5e9;
            border-radius: 4px;
            margin-top: 5px;
            font-family: monospace;
        }}

        .risk-cell {{
            max-width: 300px;
            font-size: 0.95em;
            color: #495057;
        }}

        .actions-cell {{
            max-width: 400px;
        }}

        .actions-list {{
            margin-left: 20px;
            font-size: 0.9em;
            line-height: 1.6;
        }}

        .actions-list li {{
            margin-bottom: 8px;
        }}

        .footer {{
            padding: 30px;
            text-align: center;
            background: #f8f9fa;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ License Change Alert</h1>

            <div class="alert-box">
                <h2>🚨 {len(changes)} License Changes Detected</h2>
                <p>Critical: {sum(1 for c in changes if c.severity == 'critical')} |
                   High: {sum(1 for c in changes if c.severity == 'high')} |
                   Medium: {sum(1 for c in changes if c.severity == 'medium')} |
                   Low: {sum(1 for c in changes if c.severity == 'low')}</p>
            </div>
        </div>

        <div class="content">
            <table>
                <thead>
                    <tr>
                        <th>Severity</th>
                        <th>Package</th>
                        <th>License Change</th>
                        <th>Date</th>
                        <th>Risk Assessment</th>
                        <th>Recommended Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {change_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p><strong>⚠️ IMPORTANT: Review all changes before proceeding with builds or deployments</strong></p>
            <p>Generated: {datetime.now().isoformat()}</p>
        </div>
    </div>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ License change report generated: {output_file}")

    def _get_severity_icon(self, severity: str) -> str:
        """Get emoji icon for severity"""
        icons = {
            ChangeSeverity.CRITICAL: '⛔',
            ChangeSeverity.HIGH: '⚠️',
            ChangeSeverity.MEDIUM: '📋',
            ChangeSeverity.LOW: 'ℹ️'
        }
        return icons.get(severity, '❓')

    def get_package_history(self, package_id: str) -> Optional[Dict]:
        """Get full history for a specific package"""
        return self.history['packages'].get(package_id)

    def export_history(self, output_file: str):
        """Export full history to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2)

        print(f"✅ History exported to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='License Change Monitor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize tracking
  python license_change_monitor.py --init \\
    --ort-results ort-results/analyzer/analyzer-result.yml

  # Check for changes
  python license_change_monitor.py --check \\
    --ort-results ort-results/analyzer/analyzer-result.yml \\
    --output license-changes-report.html

  # With policy file for severity assessment
  python license_change_monitor.py --check \\
    --ort-results ort-results/analyzer/analyzer-result.yml \\
    --policy config/company-policy.yml \\
    --output license-changes-report.html
        """
    )

    parser.add_argument('--init', action='store_true', help='Initialize tracking')
    parser.add_argument('--check', action='store_true', help='Check for changes')
    parser.add_argument('--ort-results', required=True, help='ORT analyzer-result.yml file')
    parser.add_argument('--history', default='.ort/license-history.json', help='History file')
    parser.add_argument('--policy', help='Policy file for severity assessment')
    parser.add_argument('--output', default='license-changes-report.html', help='Output HTML file')
    parser.add_argument('--fail-on-critical', action='store_true', help='Exit with error if critical changes found')

    args = parser.parse_args()

    if not args.init and not args.check:
        print("❌ Must specify either --init or --check")
        sys.exit(1)

    print("🔍 License Change Monitor")
    print("=" * 60)

    # Initialize monitor
    monitor = LicenseChangeMonitor(
        history_file=args.history,
        policy_file=args.policy
    )

    if args.init:
        # Initialize tracking
        monitor.initialize_tracking(args.ort_results)

    if args.check:
        # Check for changes
        changes = monitor.check_for_changes(args.ort_results)

        print(f"\n📊 Results:")
        print(f"   Total changes detected: {len(changes)}")

        if changes:
            critical = sum(1 for c in changes if c.severity == ChangeSeverity.CRITICAL)
            high = sum(1 for c in changes if c.severity == ChangeSeverity.HIGH)
            medium = sum(1 for c in changes if c.severity == ChangeSeverity.MEDIUM)
            low = sum(1 for c in changes if c.severity == ChangeSeverity.LOW)

            print(f"   ⛔ Critical: {critical}")
            print(f"   ⚠️  High:     {high}")
            print(f"   📋 Medium:   {medium}")
            print(f"   ℹ️  Low:      {low}")

            # Generate report
            monitor.generate_html_report(changes, args.output)

            # Fail on critical if requested
            if args.fail_on_critical and critical > 0:
                print(f"\n❌ CRITICAL LICENSE CHANGES DETECTED!")
                print(f"   Review {args.output} before proceeding")
                sys.exit(1)

        else:
            print("   ✅ No license changes detected")

    print("\n" + "=" * 60)
    print("✅ License change monitoring complete")


if __name__ == '__main__':
    main()
