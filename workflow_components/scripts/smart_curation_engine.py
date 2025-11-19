#!/usr/bin/env python3
"""
Smart Curation Engine - Combines all analysis results to generate intelligent curation suggestions

This script consolidates data from:
- Policy Checker (policy compliance)
- License Change Monitor (historical changes)
- Alternative Package Finder (replacement suggestions)
- Multi-tool analysis (ORT + PyPI + ScanCode + AI)

Outputs:
- Smart curation suggestions (.ort/curations.yml format)
- Confidence scores for each suggestion
- Evidence-based recommendations
- Manual review queue (HTML report)
"""

import argparse
import json
import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re


class SmartCurationEngine:
    """Intelligent curation suggestion engine"""

    def __init__(self, policy_file: str):
        self.policy = self._load_policy(policy_file)
        self.curations = []
        self.manual_review = []
        self.evidence_db = {}

    def _load_policy(self, policy_file: str) -> dict:
        """Load company policy"""
        try:
            with open(policy_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️  Warning: Could not load policy file: {e}")
            return {}

    def _normalize_license(self, license_str: str) -> str:
        """Normalize license string to SPDX identifier"""
        if not license_str:
            return "NOASSERTION"

        # Common normalizations
        normalizations = {
            "UNKNOWN": "NOASSERTION",
            "NONE": "NOASSERTION",
            "": "NOASSERTION",
            "BSD License": "BSD-3-Clause",
            "BSD": "BSD-3-Clause",
            "Apache License 2.0": "Apache-2.0",
            "Apache 2.0": "Apache-2.0",
            "MIT License": "MIT",
            "GNU GPL": "GPL-3.0-or-later",
            "GPLv2": "GPL-2.0-only",
            "GPLv3": "GPL-3.0-only",
        }

        return normalizations.get(license_str, license_str)

    def load_policy_results(self, policy_json: str):
        """Load policy compliance results"""
        try:
            with open(policy_json, 'r') as f:
                data = json.load(f)

            print(f"✅ Loaded policy results: {len(data.get('packages', []))} packages")

            for pkg in data.get('packages', []):
                pkg_id = pkg.get('id')
                status = pkg.get('status')

                if pkg_id not in self.evidence_db:
                    self.evidence_db[pkg_id] = {
                        'policy_status': status,
                        'licenses': {},
                        'confidence': 0,
                        'sources': []
                    }
                else:
                    self.evidence_db[pkg_id]['policy_status'] = status

                # Add policy check as evidence
                if status == 'APPROVED':
                    self.evidence_db[pkg_id]['confidence'] += 0.3
                    self.evidence_db[pkg_id]['sources'].append('policy_approved')
                elif status == 'FORBIDDEN':
                    self.evidence_db[pkg_id]['confidence'] = 0
                    self.evidence_db[pkg_id]['sources'].append('policy_forbidden')

        except Exception as e:
            print(f"⚠️  Warning: Could not load policy results: {e}")

    def load_ort_results(self, ort_file: str):
        """Load ORT analyzer results"""
        try:
            with open(ort_file, 'r') as f:
                data = yaml.safe_load(f)

            packages = data.get('analyzer', {}).get('result', {}).get('packages', [])
            print(f"✅ Loaded ORT results: {len(packages)} packages")

            for pkg in packages:
                pkg_id = pkg.get('id', '')
                declared = pkg.get('declared_licenses', [])
                concluded = pkg.get('concluded_license')

                if pkg_id not in self.evidence_db:
                    self.evidence_db[pkg_id] = {
                        'policy_status': 'UNKNOWN',
                        'licenses': {},
                        'confidence': 0,
                        'sources': []
                    }

                # Add ORT evidence
                if declared:
                    for lic in declared:
                        if lic not in self.evidence_db[pkg_id]['licenses']:
                            self.evidence_db[pkg_id]['licenses'][lic] = {'sources': [], 'confidence': 0}
                        self.evidence_db[pkg_id]['licenses'][lic]['sources'].append('ORT_declared')
                        self.evidence_db[pkg_id]['licenses'][lic]['confidence'] += 0.4

                if concluded and concluded != 'NOASSERTION':
                    normalized = self._normalize_license(concluded)
                    if normalized not in self.evidence_db[pkg_id]['licenses']:
                        self.evidence_db[pkg_id]['licenses'][normalized] = {'sources': [], 'confidence': 0}
                    self.evidence_db[pkg_id]['licenses'][normalized]['sources'].append('ORT_concluded')
                    self.evidence_db[pkg_id]['licenses'][normalized]['confidence'] += 0.5

        except Exception as e:
            print(f"⚠️  Warning: Could not load ORT results: {e}")

    def load_pypi_results(self, pypi_json: str):
        """Load PyPI license fetch results"""
        try:
            with open(pypi_json, 'r') as f:
                data = json.load(f)

            packages = data.get('packages', [])
            print(f"✅ Loaded PyPI results: {len(packages)} packages")

            for pkg in packages:
                pkg_name = pkg.get('package_name')
                pkg_version = pkg.get('version')
                license_found = pkg.get('license_from_pypi')

                # Construct package ID (PyPI format)
                pkg_id = f"PyPI::{pkg_name}:{pkg_version}"

                if pkg_id not in self.evidence_db:
                    self.evidence_db[pkg_id] = {
                        'policy_status': 'UNKNOWN',
                        'licenses': {},
                        'confidence': 0,
                        'sources': []
                    }

                if license_found and license_found != 'Not found':
                    normalized = self._normalize_license(license_found)
                    if normalized not in self.evidence_db[pkg_id]['licenses']:
                        self.evidence_db[pkg_id]['licenses'][normalized] = {'sources': [], 'confidence': 0}
                    self.evidence_db[pkg_id]['licenses'][normalized]['sources'].append('PyPI_API')
                    self.evidence_db[pkg_id]['licenses'][normalized]['confidence'] += 0.3

        except Exception as e:
            print(f"⚠️  Warning: Could not load PyPI results: {e}")

    def load_scancode_results(self, scancode_dir: str):
        """Load ScanCode scan results"""
        try:
            scancode_path = Path(scancode_dir)
            if not scancode_path.exists():
                return

            json_files = list(scancode_path.glob('*.json'))
            print(f"✅ Loading ScanCode results: {len(json_files)} packages")

            for json_file in json_files:
                with open(json_file, 'r') as f:
                    data = json.load(f)

                # Extract package name from filename
                pkg_name = json_file.stem

                # Find licenses in scan
                licenses_found = {}
                for file_data in data.get('files', []):
                    for lic in file_data.get('licenses', []):
                        lic_key = lic.get('key', 'unknown')
                        score = lic.get('score', 0)

                        if score >= 80:  # High confidence only
                            if lic_key not in licenses_found:
                                licenses_found[lic_key] = {'count': 0, 'max_score': 0}
                            licenses_found[lic_key]['count'] += 1
                            licenses_found[lic_key]['max_score'] = max(
                                licenses_found[lic_key]['max_score'],
                                score
                            )

                # Add to evidence
                for pkg_id, evidence in self.evidence_db.items():
                    if pkg_name.lower() in pkg_id.lower():
                        for lic_key, stats in licenses_found.items():
                            if lic_key not in evidence['licenses']:
                                evidence['licenses'][lic_key] = {'sources': [], 'confidence': 0}
                            evidence['licenses'][lic_key]['sources'].append('ScanCode')
                            # Confidence based on detection count and score
                            confidence_boost = min(0.4, stats['count'] * 0.05 + stats['max_score'] / 200)
                            evidence['licenses'][lic_key]['confidence'] += confidence_boost

        except Exception as e:
            print(f"⚠️  Warning: Could not load ScanCode results: {e}")

    def generate_curations(self) -> List[dict]:
        """Generate smart curation suggestions based on all evidence"""
        curations = []

        for pkg_id, evidence in self.evidence_db.items():
            # Skip packages that are already policy-approved with high confidence
            if evidence.get('policy_status') == 'APPROVED' and evidence.get('confidence', 0) > 0.7:
                continue

            # Skip forbidden packages (need alternatives, not curations)
            if evidence.get('policy_status') == 'FORBIDDEN':
                continue

            # Find best license candidate
            best_license = self._select_best_license(pkg_id, evidence)

            if best_license:
                curation = {
                    'id': pkg_id,
                    'curations': {
                        'concluded_license': best_license['license'],
                        'comment': best_license['comment']
                    },
                    'confidence': best_license['confidence'],
                    'sources': best_license['sources'],
                    'requires_manual_review': best_license['confidence'] < 0.7
                }

                curations.append(curation)

                if curation['requires_manual_review']:
                    self.manual_review.append(curation)

        return curations

    def _select_best_license(self, pkg_id: str, evidence: dict) -> Optional[dict]:
        """Select the best license based on multi-source evidence"""
        licenses = evidence.get('licenses', {})

        if not licenses:
            return None

        # Score each license candidate
        candidates = []
        for lic, lic_data in licenses.items():
            # Skip NOASSERTION
            if lic == 'NOASSERTION':
                continue

            confidence = lic_data.get('confidence', 0)
            sources = lic_data.get('sources', [])

            # Check if approved by policy
            is_approved = self._is_license_approved(lic)

            # Bonus for policy approval
            if is_approved:
                confidence += 0.2

            # Bonus for multiple sources
            if len(sources) > 1:
                confidence += 0.1 * len(sources)

            # Cap at 1.0
            confidence = min(1.0, confidence)

            candidates.append({
                'license': lic,
                'confidence': confidence,
                'sources': sources,
                'approved': is_approved
            })

        if not candidates:
            return None

        # Sort by confidence, prefer approved licenses
        candidates.sort(key=lambda x: (x['approved'], x['confidence']), reverse=True)
        best = candidates[0]

        # Generate comment
        comment = f"License detected from {', '.join(best['sources'])}. "
        comment += f"Confidence: {best['confidence']:.0%}. "

        if best['confidence'] < 0.7:
            comment += "REQUIRES MANUAL VERIFICATION. "

        if best['approved']:
            comment += "Approved by company policy."
        else:
            comment += "CHECK POLICY COMPLIANCE before applying."

        return {
            'license': best['license'],
            'confidence': best['confidence'],
            'sources': best['sources'],
            'comment': comment
        }

    def _is_license_approved(self, license_str: str) -> bool:
        """Check if license is approved by company policy"""
        policy = self.policy.get('company_license_policy', {})
        approved_section = policy.get('approved_licenses', {})

        for category, data in approved_section.items():
            licenses = data.get('licenses', [])
            if license_str in licenses:
                return True

        return False

    def export_curations_yaml(self, output_file: str):
        """Export curations in ORT .ort/curations.yml format"""
        curations_yml = {
            'curations': []
        }

        for curation in self.curations:
            if not curation.get('requires_manual_review'):
                # Only export high-confidence curations
                curations_yml['curations'].append({
                    'id': curation['id'],
                    'curations': curation['curations']
                })

        with open(output_file, 'w') as f:
            yaml.dump(curations_yml, f, default_flow_style=False, sort_keys=False)

        print(f"✅ Exported {len(curations_yml['curations'])} high-confidence curations to {output_file}")

    def export_manual_review_html(self, output_file: str):
        """Export manual review queue as HTML"""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Manual Review Queue - Smart Curation Engine</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 40px;
        }
        h1 {
            color: #667eea;
            margin-top: 0;
            font-size: 2.5em;
        }
        .summary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .summary h2 {
            margin-top: 0;
        }
        .package {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            background: #f9f9f9;
        }
        .package-id {
            font-weight: bold;
            color: #333;
            font-size: 1.1em;
            margin-bottom: 10px;
        }
        .confidence-bar {
            background: #e0e0e0;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff6b6b 0%, #ffd93d 50%, #6bcf7f 100%);
            transition: width 0.3s;
        }
        .confidence-low { background: #ff6b6b !important; }
        .confidence-medium { background: #ffd93d !important; }
        .confidence-high { background: #6bcf7f !important; }
        .license-badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            margin: 5px 5px 5px 0;
            font-size: 0.9em;
        }
        .source-badge {
            display: inline-block;
            background: #764ba2;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            margin: 3px;
            font-size: 0.8em;
        }
        .comment {
            background: #fff;
            padding: 15px;
            border-left: 4px solid #667eea;
            margin: 10px 0;
            border-radius: 4px;
        }
        .action-required {
            background: #fff3cd;
            border-left-color: #ffc107;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-box {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Manual Review Queue</h1>
        <p><strong>Generated:</strong> """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>

        <div class="summary">
            <h2>📊 Summary</h2>
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-number">""" + str(len(self.manual_review)) + """</div>
                    <div class="stat-label">Packages Requiring Review</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">""" + str(len([c for c in self.manual_review if c['confidence'] < 0.5])) + """</div>
                    <div class="stat-label">Low Confidence (&lt;50%)</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">""" + str(len([c for c in self.manual_review if 0.5 <= c['confidence'] < 0.7])) + """</div>
                    <div class="stat-label">Medium Confidence (50-70%)</div>
                </div>
            </div>
        </div>

        <h2>📦 Packages Requiring Manual Verification</h2>
"""

        # Sort by confidence (lowest first - highest priority)
        sorted_reviews = sorted(self.manual_review, key=lambda x: x['confidence'])

        for curation in sorted_reviews:
            confidence_pct = int(curation['confidence'] * 100)
            confidence_class = 'confidence-low' if confidence_pct < 50 else ('confidence-medium' if confidence_pct < 70 else 'confidence-high')

            html += f"""
        <div class="package">
            <div class="package-id">📦 {curation['id']}</div>

            <div>
                <strong>Suggested License:</strong>
                <span class="license-badge">{curation['curations']['concluded_license']}</span>
            </div>

            <div style="margin: 10px 0;">
                <strong>Confidence:</strong> {confidence_pct}%
                <div class="confidence-bar">
                    <div class="confidence-fill {confidence_class}" style="width: {confidence_pct}%"></div>
                </div>
            </div>

            <div style="margin: 10px 0;">
                <strong>Evidence Sources:</strong><br>
"""
            for source in curation['sources']:
                html += f'                <span class="source-badge">{source}</span>\n'

            html += f"""
            </div>

            <div class="comment">
                <strong>💡 Comment:</strong><br>
                {curation['curations']['comment']}
            </div>

            <div class="action-required">
                <strong>⚠️ Action Required:</strong><br>
                1. Verify license from source repository (GitHub, GitLab, etc.)<br>
                2. Check package homepage and documentation<br>
                3. Review LICENSE or COPYING file in source<br>
                4. Confirm with package maintainer if uncertain<br>
                5. Update curation manually if suggestion is incorrect
            </div>
        </div>
"""

        html += """
    </div>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ Exported {len(self.manual_review)} packages requiring manual review to {output_file}")

    def export_statistics_json(self, output_file: str):
        """Export statistics as JSON"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'total_packages': len(self.evidence_db),
            'total_curations': len(self.curations),
            'high_confidence': len([c for c in self.curations if c['confidence'] >= 0.7]),
            'manual_review_required': len(self.manual_review),
            'by_policy_status': {},
            'by_confidence': {
                'high': len([c for c in self.curations if c['confidence'] >= 0.7]),
                'medium': len([c for c in self.curations if 0.5 <= c['confidence'] < 0.7]),
                'low': len([c for c in self.curations if c['confidence'] < 0.5])
            }
        }

        # Count by policy status
        for pkg_id, evidence in self.evidence_db.items():
            status = evidence.get('policy_status', 'UNKNOWN')
            stats['by_policy_status'][status] = stats['by_policy_status'].get(status, 0) + 1

        with open(output_file, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"✅ Exported statistics to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Smart Curation Engine - Generate intelligent curation suggestions'
    )
    parser.add_argument('--policy', required=True, help='Company policy YAML file')
    parser.add_argument('--ort-results', help='ORT analyzer results YAML file')
    parser.add_argument('--policy-json', help='Policy checker results JSON file')
    parser.add_argument('--pypi-json', help='PyPI fetch results JSON file')
    parser.add_argument('--scancode-dir', help='Directory containing ScanCode JSON files')
    parser.add_argument('--output-curations', default='smart-curations.yml',
                       help='Output file for suggested curations (YAML)')
    parser.add_argument('--output-review', default='manual-review-queue.html',
                       help='Output file for manual review queue (HTML)')
    parser.add_argument('--output-stats', default='curation-stats.json',
                       help='Output file for statistics (JSON)')

    args = parser.parse_args()

    print("🤖 Smart Curation Engine")
    print("=" * 60)

    # Initialize engine
    engine = SmartCurationEngine(args.policy)

    # Load all available data sources
    if args.policy_json:
        print("\n📊 Loading policy compliance results...")
        engine.load_policy_results(args.policy_json)

    if args.ort_results:
        print("\n📦 Loading ORT analyzer results...")
        engine.load_ort_results(args.ort_results)

    if args.pypi_json:
        print("\n🐍 Loading PyPI fetch results...")
        engine.load_pypi_results(args.pypi_json)

    if args.scancode_dir:
        print("\n🔬 Loading ScanCode scan results...")
        engine.load_scancode_results(args.scancode_dir)

    # Generate curations
    print("\n🧠 Generating smart curation suggestions...")
    engine.curations = engine.generate_curations()

    print(f"\n✅ Generated {len(engine.curations)} curation suggestions")
    print(f"   - High confidence (≥70%): {len([c for c in engine.curations if c['confidence'] >= 0.7])}")
    print(f"   - Manual review required: {len(engine.manual_review)}")

    # Export results
    print("\n📄 Exporting results...")
    engine.export_curations_yaml(args.output_curations)
    engine.export_manual_review_html(args.output_review)
    engine.export_statistics_json(args.output_stats)

    print("\n" + "=" * 60)
    print("✅ Smart Curation Engine completed successfully!")
    print("\nNext steps:")
    print(f"1. Review manual verification queue: {args.output_review}")
    print(f"2. Verify high-confidence curations: {args.output_curations}")
    print(f"3. Apply curations to .ort/curations.yml after verification")
    print("\n⚠️  IMPORTANT: Always manually verify curations before applying to production!")

    return 0


if __name__ == '__main__':
    sys.exit(main())
