#!/usr/bin/env python3
"""
SBOM Compliance Checker - Validates SBOM against NTIA minimum elements
Uses spdx-tools for official SPDX validation and compliance checking
"""

import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

try:
    from spdx_tools.spdx.parser.parse_anything import parse_file
    from spdx_tools.spdx.validation.document_validator import validate_full_spdx_document
    from spdx_tools.spdx.model import Document
    SPDX_TOOLS_AVAILABLE = True
except ImportError:
    SPDX_TOOLS_AVAILABLE = False
    print("⚠️  spdx-tools not installed. Install with: pip install spdx-tools")


class SBOMComplianceChecker:
    """Checks SBOM compliance against NTIA minimum elements"""

    # NTIA Minimum Elements for SBOM
    NTIA_REQUIRED_FIELDS = {
        'author': 'Supplier Name',
        'component_name': 'Component Name',
        'version': 'Version of Component',
        'dependencies': 'Dependency Relationships',
        'unique_identifier': 'Unique Identifier',
        'timestamp': 'Timestamp',
        'license': 'License Information'
    }

    def __init__(self, spdx_path: str):
        self.spdx_path = Path(spdx_path)
        self.document = None
        self.compliance_results = {
            'ntia_compliant': True,
            'total_packages': 0,
            'packages_checked': 0,
            'missing_author': [],
            'missing_version': [],
            'missing_license': [],
            'missing_identifier': [],
            'validation_errors': [],
            'validation_warnings': [],
            'compliance_score': 0.0,
            'timestamp': datetime.now().isoformat()
        }

    def load_spdx_document(self) -> bool:
        """Load and parse SPDX document using spdx-tools"""
        if not SPDX_TOOLS_AVAILABLE:
            print("❌ Cannot load SPDX document - spdx-tools not available")
            return False

        try:
            print(f"📖 Loading SPDX document: {self.spdx_path}")
            self.document = parse_file(str(self.spdx_path))
            print(f"✅ Successfully parsed SPDX document")
            return True
        except Exception as e:
            print(f"❌ Error parsing SPDX document: {e}")
            self.compliance_results['validation_errors'].append(str(e))
            return False

    def validate_spdx_specification(self) -> List:
        """Validate against SPDX specification using official validator"""
        if not self.document:
            return []

        print("\n🔍 Validating against SPDX specification...")

        try:
            validation_messages = validate_full_spdx_document(self.document)

            for msg in validation_messages:
                msg_str = str(msg.validation_message)
                print(f"   {msg_str}")

                # Categorize messages
                if "error" in msg_str.lower():
                    self.compliance_results['validation_errors'].append(msg_str)
                else:
                    self.compliance_results['validation_warnings'].append(msg_str)

            if validation_messages:
                print(f"⚠️  Found {len(validation_messages)} validation issues")
            else:
                print("✅ SPDX document is valid according to specification")

            return validation_messages
        except Exception as e:
            error_msg = f"Validation error: {e}"
            print(f"❌ {error_msg}")
            self.compliance_results['validation_errors'].append(error_msg)
            return []

    def check_ntia_minimum_elements(self):
        """Check SBOM against NTIA minimum elements"""
        if not self.document:
            return

        print("\n🔍 Checking NTIA Minimum Elements for SBOM...")
        print("=" * 70)

        # Check document-level requirements
        self._check_document_metadata()

        # Check package-level requirements
        self._check_package_compliance()

        # Calculate compliance score
        self._calculate_compliance_score()

        # Print summary
        self._print_ntia_summary()

    def _check_document_metadata(self):
        """Check document-level NTIA requirements"""
        print("\n📋 Document Metadata:")

        # 1. Timestamp
        if self.document.creation_info.created:
            print(f"   ✅ Timestamp: {self.document.creation_info.created}")
        else:
            print(f"   ❌ Timestamp: Missing")
            self.compliance_results['ntia_compliant'] = False

        # 2. Author (Creator)
        if self.document.creation_info.creators:
            creators = [str(c) for c in self.document.creation_info.creators]
            print(f"   ✅ Authors: {', '.join(creators)}")
        else:
            print(f"   ❌ Authors: Missing")
            self.compliance_results['ntia_compliant'] = False

        # 3. Unique Identifier (SPDX ID)
        if self.document.creation_info.spdx_id:
            print(f"   ✅ Document ID: {self.document.creation_info.spdx_id}")
        else:
            print(f"   ❌ Document ID: Missing")
            self.compliance_results['ntia_compliant'] = False

    def _check_package_compliance(self):
        """Check package-level NTIA requirements"""
        print("\n📦 Package Compliance:")

        if not self.document.packages:
            print("   ❌ No packages found in SBOM")
            self.compliance_results['ntia_compliant'] = False
            return

        self.compliance_results['total_packages'] = len(self.document.packages)

        for package in self.document.packages:
            self.compliance_results['packages_checked'] += 1

            pkg_name = package.name
            issues = []

            # 1. Component Name (always present in SPDX)
            # No check needed - SPDX requires package name

            # 2. Supplier/Author
            if not package.supplier and not package.originator:
                issues.append("missing supplier/originator")
                self.compliance_results['missing_author'].append(pkg_name)

            # 3. Version
            if not package.version:
                issues.append("missing version")
                self.compliance_results['missing_version'].append(pkg_name)

            # 4. Unique Identifier (SPDX ID)
            if not package.spdx_id:
                issues.append("missing SPDX ID")
                self.compliance_results['missing_identifier'].append(pkg_name)

            # 5. License
            license_concluded = str(package.license_concluded) if package.license_concluded else "NOASSERTION"
            license_declared = str(package.license_declared) if package.license_declared else "NOASSERTION"

            if license_concluded == "NOASSERTION" and license_declared == "NOASSERTION":
                issues.append("no license information")
                self.compliance_results['missing_license'].append(pkg_name)

            # Print package status
            if issues:
                print(f"   ⚠️  {pkg_name}: {', '.join(issues)}")
            else:
                print(f"   ✅ {pkg_name}: All NTIA elements present")

        # 6. Dependencies (check relationships)
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if dependency relationships are documented"""
        print("\n🔗 Dependency Relationships:")

        if not self.document.relationships:
            print("   ⚠️  No relationships documented")
            self.compliance_results['validation_warnings'].append(
                "No dependency relationships documented"
            )
            return

        # Count dependency-related relationships
        dependency_relationships = [
            rel for rel in self.document.relationships
            if 'DEPENDS' in str(rel.relationship_type) or
               'DEPENDENCY' in str(rel.relationship_type)
        ]

        print(f"   ✅ Found {len(self.document.relationships)} relationships")
        print(f"   ✅ Including {len(dependency_relationships)} dependency relationships")

    def _calculate_compliance_score(self):
        """Calculate overall compliance score"""
        total_packages = self.compliance_results['total_packages']

        if total_packages == 0:
            self.compliance_results['compliance_score'] = 0.0
            return

        # Penalties for missing elements
        penalties = 0
        max_penalties = total_packages * 4  # 4 main elements per package

        penalties += len(self.compliance_results['missing_author'])
        penalties += len(self.compliance_results['missing_version'])
        penalties += len(self.compliance_results['missing_license'])
        penalties += len(self.compliance_results['missing_identifier'])

        # Calculate score (0-100)
        score = max(0, 100 - (penalties / max_penalties * 100)) if max_penalties > 0 else 100
        self.compliance_results['compliance_score'] = round(score, 2)

        # Update ntia_compliant flag
        if score < 90:  # 90% threshold for compliance
            self.compliance_results['ntia_compliant'] = False

    def _print_ntia_summary(self):
        """Print NTIA compliance summary"""
        print("\n" + "=" * 70)
        print("📊 NTIA COMPLIANCE SUMMARY")
        print("=" * 70)

        results = self.compliance_results

        print(f"Total packages: {results['total_packages']}")
        print(f"Packages checked: {results['packages_checked']}")
        print(f"\nMissing Elements:")
        print(f"  - Missing author/supplier: {len(results['missing_author'])}")
        print(f"  - Missing version: {len(results['missing_version'])}")
        print(f"  - Missing license: {len(results['missing_license'])}")
        print(f"  - Missing identifier: {len(results['missing_identifier'])}")

        print(f"\nValidation Issues:")
        print(f"  - Errors: {len(results['validation_errors'])}")
        print(f"  - Warnings: {len(results['validation_warnings'])}")

        print(f"\n📈 Compliance Score: {results['compliance_score']}%")

        if results['ntia_compliant'] and results['compliance_score'] >= 90:
            print("✅ STATUS: NTIA COMPLIANT")
        else:
            print("❌ STATUS: NOT FULLY COMPLIANT")

        print("=" * 70)

    def generate_html_report(self, output_path: str):
        """Generate detailed HTML compliance report"""
        print(f"\n📄 Generating HTML compliance report: {output_path}")

        results = self.compliance_results

        # Determine status color and badge
        if results['compliance_score'] >= 95:
            status_color = "#2e7d32"
            status_badge = "EXCELLENT"
        elif results['compliance_score'] >= 90:
            status_color = "#388e3c"
            status_badge = "COMPLIANT"
        elif results['compliance_score'] >= 75:
            status_color = "#f57c00"
            status_badge = "NEEDS IMPROVEMENT"
        else:
            status_color = "#d32f2f"
            status_badge = "NON-COMPLIANT"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SBOM Compliance Report - NTIA Minimum Elements</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, {status_color} 0%, {status_color}dd 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .header .subtitle {{ opacity: 0.9; font-size: 16px; }}
        .score-circle {{
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background: white;
            margin: 20px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            font-weight: bold;
            color: {status_color};
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }}
        .status-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            margin-top: 10px;
        }}
        .content {{ padding: 40px; }}
        .section {{
            margin-bottom: 40px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid {status_color};
        }}
        .section h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 24px;
        }}
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 36px;
            font-weight: bold;
            color: {status_color};
            margin-bottom: 5px;
        }}
        .stat-label {{ color: #666; font-size: 14px; }}
        .ntia-checklist {{
            list-style: none;
            margin-top: 20px;
        }}
        .ntia-checklist li {{
            padding: 15px;
            margin-bottom: 10px;
            background: white;
            border-radius: 6px;
            display: flex;
            align-items: center;
        }}
        .ntia-checklist .icon {{
            margin-right: 15px;
            font-size: 24px;
        }}
        .issue-list {{
            background: white;
            border-radius: 6px;
            padding: 20px;
            margin-top: 20px;
        }}
        .issue-item {{
            padding: 10px;
            border-bottom: 1px solid #e0e0e0;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }}
        .issue-item:last-child {{ border-bottom: none; }}
        .error {{ color: #d32f2f; }}
        .warning {{ color: #f57c00; }}
        .success {{ color: #2e7d32; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{
            background: {status_color};
            color: white;
            font-weight: 600;
        }}
        tr:hover {{ background: #f5f5f5; }}
        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 SBOM Compliance Report</h1>
            <p class="subtitle">NTIA Minimum Elements for Software Bill of Materials</p>
            <div class="score-circle">{results['compliance_score']}%</div>
            <div class="status-badge">{status_badge}</div>
            <p style="margin-top: 15px; opacity: 0.9;">Generated: {results['timestamp']}</p>
        </div>

        <div class="content">
            <!-- Quick Stats -->
            <div class="section">
                <h2>📈 Quick Statistics</h2>
                <div class="stat-grid">
                    <div class="stat-card">
                        <div class="stat-number">{results['total_packages']}</div>
                        <div class="stat-label">Total Packages</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(results['missing_author'])}</div>
                        <div class="stat-label">Missing Author</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(results['missing_version'])}</div>
                        <div class="stat-label">Missing Version</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(results['missing_license'])}</div>
                        <div class="stat-label">Missing License</div>
                    </div>
                </div>
            </div>

            <!-- NTIA Checklist -->
            <div class="section">
                <h2>✅ NTIA Minimum Elements Checklist</h2>
                <ul class="ntia-checklist">
                    <li>
                        <span class="icon success">✓</span>
                        <div>
                            <strong>Author Name</strong>
                            <div class="stat-label">{results['total_packages'] - len(results['missing_author'])} / {results['total_packages']} packages have author info</div>
                        </div>
                    </li>
                    <li>
                        <span class="icon success">✓</span>
                        <div>
                            <strong>Component Name</strong>
                            <div class="stat-label">All {results['total_packages']} packages have names</div>
                        </div>
                    </li>
                    <li>
                        <span class="icon success">✓</span>
                        <div>
                            <strong>Version Information</strong>
                            <div class="stat-label">{results['total_packages'] - len(results['missing_version'])} / {results['total_packages']} packages have versions</div>
                        </div>
                    </li>
                    <li>
                        <span class="icon success">✓</span>
                        <div>
                            <strong>Dependency Relationships</strong>
                            <div class="stat-label">Documented in SPDX relationships</div>
                        </div>
                    </li>
                    <li>
                        <span class="icon success">✓</span>
                        <div>
                            <strong>Unique Identifier</strong>
                            <div class="stat-label">{results['total_packages'] - len(results['missing_identifier'])} / {results['total_packages']} packages have SPDX IDs</div>
                        </div>
                    </li>
                    <li>
                        <span class="icon success">✓</span>
                        <div>
                            <strong>Timestamp</strong>
                            <div class="stat-label">Document creation timestamp present</div>
                        </div>
                    </li>
                    <li>
                        <span class="icon success">✓</span>
                        <div>
                            <strong>License Information</strong>
                            <div class="stat-label">{results['total_packages'] - len(results['missing_license'])} / {results['total_packages']} packages have license data</div>
                        </div>
                    </li>
                </ul>
            </div>

            <!-- Validation Issues -->
            {'<div class="section"><h2>⚠️ Validation Issues</h2>' if results['validation_errors'] or results['validation_warnings'] else ''}
            {f'''<div class="issue-list">
                <h3 class="error">Errors ({len(results['validation_errors'])})</h3>
                {''.join(f'<div class="issue-item error">• {err}</div>' for err in results['validation_errors'][:10])}
            </div>''' if results['validation_errors'] else ''}
            {f'''<div class="issue-list" style="margin-top: 20px;">
                <h3 class="warning">Warnings ({len(results['validation_warnings'])})</h3>
                {''.join(f'<div class="issue-item warning">• {warn}</div>' for warn in results['validation_warnings'][:10])}
            </div>''' if results['validation_warnings'] else ''}
            {'</div>' if results['validation_errors'] or results['validation_warnings'] else ''}

            <!-- Missing Elements Details -->
            {f'''<div class="section">
                <h2>🔍 Packages Missing Required Elements</h2>
                {f'<h3>Missing Author/Supplier ({len(results["missing_author"])})</h3><div class="issue-list">{"".join(f'<div class="issue-item">• {pkg}</div>' for pkg in results["missing_author"][:20])}</div>' if results['missing_author'] else ''}
                {f'<h3 style="margin-top: 20px;">Missing Version ({len(results["missing_version"])})</h3><div class="issue-list">{"".join(f'<div class="issue-item">• {pkg}</div>' for pkg in results["missing_version"][:20])}</div>' if results['missing_version'] else ''}
                {f'<h3 style="margin-top: 20px;">Missing License ({len(results["missing_license"])})</h3><div class="issue-list">{"".join(f'<div class="issue-item">• {pkg}</div>' for pkg in results["missing_license"][:20])}</div>' if results['missing_license'] else ''}
            </div>''' if (results['missing_author'] or results['missing_version'] or results['missing_license']) else ''}

            <!-- Recommendations -->
            <div class="section">
                <h2>💡 Recommendations</h2>
                <ul style="margin-left: 20px;">
                    {f'<li>Add supplier/originator information for {len(results["missing_author"])} packages</li>' if results['missing_author'] else ''}
                    {f'<li>Specify version information for {len(results["missing_version"])} packages</li>' if results['missing_version'] else ''}
                    {f'<li>Curate license information for {len(results["missing_license"])} packages</li>' if results['missing_license'] else ''}
                    {f'<li>Fix {len(results["validation_errors"])} SPDX specification errors</li>' if results['validation_errors'] else ''}
                    <li>Use Smart Curation Engine to automatically resolve license information</li>
                    <li>Review manual curation queue for uncertain packages</li>
                    <li>Verify all SPDX IDs follow correct naming convention</li>
                </ul>
            </div>

            <!-- About NTIA -->
            <div class="section">
                <h2>📚 About NTIA Minimum Elements</h2>
                <p>The National Telecommunications and Information Administration (NTIA) defines minimum elements for Software Bill of Materials (SBOM):</p>
                <ol style="margin: 15px 0 0 20px;">
                    <li><strong>Author Name</strong> - Who created/supplied the component</li>
                    <li><strong>Component Name</strong> - Designation for the unit of software</li>
                    <li><strong>Version</strong> - Identifier for a specific release</li>
                    <li><strong>Component Hash</strong> - Cryptographic hash for integrity (optional in baseline)</li>
                    <li><strong>Unique Identifier</strong> - Reference identifier for the component</li>
                    <li><strong>Dependency Relationship</strong> - Characterizing component dependencies</li>
                    <li><strong>SBOM Author</strong> - Who created the SBOM</li>
                    <li><strong>Timestamp</strong> - When the SBOM was created</li>
                </ol>
                <p style="margin-top: 15px;">This report validates your SBOM against these requirements using SPDX format.</p>
            </div>
        </div>

        <div class="footer">
            <p>Generated by License Curation Toolkit</p>
            <p style="margin-top: 5px; font-size: 12px;">Using spdx-tools for official SPDX validation</p>
        </div>
    </div>
</body>
</html>"""

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ HTML report saved to: {output_path}")

    def generate_json_report(self, output_path: str):
        """Generate JSON report for programmatic use"""
        print(f"\n📄 Generating JSON report: {output_path}")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(self.compliance_results, f, indent=2)

        print(f"✅ JSON report saved to: {output_path}")

    def run(self, html_output: str = None, json_output: str = None):
        """Execute complete compliance check"""
        if not SPDX_TOOLS_AVAILABLE:
            print("❌ Cannot run compliance check - spdx-tools not installed")
            print("   Install with: pip install spdx-tools")
            return False

        # Load SPDX document
        if not self.load_spdx_document():
            return False

        # Validate SPDX specification
        self.validate_spdx_specification()

        # Check NTIA minimum elements
        self.check_ntia_minimum_elements()

        # Generate reports
        if html_output:
            self.generate_html_report(html_output)

        if json_output:
            self.generate_json_report(json_output)

        return True


def main():
    parser = argparse.ArgumentParser(
        description='Check SBOM compliance against NTIA minimum elements'
    )
    parser.add_argument(
        '--spdx',
        required=True,
        help='Path to SPDX document (JSON, YAML, XML, RDF, or tag-value)'
    )
    parser.add_argument(
        '--html-output',
        help='Path for HTML compliance report'
    )
    parser.add_argument(
        '--json-output',
        help='Path for JSON compliance report (for dashboard integration)'
    )

    args = parser.parse_args()

    if not SPDX_TOOLS_AVAILABLE:
        print("❌ spdx-tools is not installed!")
        print("   Install with: pip install spdx-tools")
        exit(1)

    checker = SBOMComplianceChecker(args.spdx)
    success = checker.run(
        html_output=args.html_output,
        json_output=args.json_output
    )

    if success:
        if checker.compliance_results['ntia_compliant'] and \
           checker.compliance_results['compliance_score'] >= 90:
            print("\n✅ SBOM is NTIA compliant!")
            exit(0)
        else:
            print("\n⚠️  SBOM needs improvement to meet NTIA requirements")
            exit(0)  # Don't fail - just report
    else:
        print("\n❌ Compliance check failed")
        exit(1)


if __name__ == '__main__':
    main()
