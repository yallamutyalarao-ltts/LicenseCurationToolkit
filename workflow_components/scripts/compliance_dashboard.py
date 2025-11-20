#!/usr/bin/env python3
"""
Compliance Dashboard Generator - Unified HTML dashboard for license compliance

Consolidates all compliance reports into a single executive dashboard:
- Policy compliance status
- License change alerts
- Alternative package suggestions
- Smart curation recommendations
- Overall compliance metrics
- Action items and priorities
- Risk assessment
"""

import argparse
import json
import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import re


class ComplianceDashboard:
    """Generate unified compliance dashboard"""

    def __init__(self):
        self.data = {
            'timestamp': datetime.now(),
            'policy': {},
            'changes': {},
            'alternatives': {},
            'curations': {},
            'sbom': {},
            'overall': {},
            'action_items': [],
            'reports': []
        }

    def load_policy_results(self, policy_json: str):
        """Load policy compliance results"""
        try:
            with open(policy_json, 'r') as f:
                data = json.load(f)

            summary = data.get('summary', {})
            self.data['policy'] = {
                'total': summary.get('total', 0),
                'approved': summary.get('approved', 0),
                'conditional': summary.get('conditional', 0),
                'forbidden': summary.get('forbidden', 0),
                'unknown': summary.get('unknown', 0),
                'compliance_score': summary.get('compliance_score', 0),
                'packages': data.get('packages', [])
            }

            print(f"✅ Loaded policy results: {self.data['policy']['total']} packages")

            # Generate action items for forbidden packages
            for pkg in self.data['policy']['packages']:
                if pkg.get('status') == 'FORBIDDEN':
                    self.data['action_items'].append({
                        'priority': 'CRITICAL',
                        'type': 'Forbidden License',
                        'package': pkg.get('id'),
                        'action': f"Replace package using {pkg.get('license')} license",
                        'deadline': 'Immediate'
                    })

            # Generate action items for conditional packages
            for pkg in self.data['policy']['packages']:
                if pkg.get('status') == 'CONDITIONAL':
                    self.data['action_items'].append({
                        'priority': 'HIGH',
                        'type': 'Approval Required',
                        'package': pkg.get('id'),
                        'action': f"Request approval for {pkg.get('license')} license",
                        'deadline': '48 hours'
                    })

        except Exception as e:
            print(f"⚠️  Warning: Could not load policy results: {e}")

    def load_change_results(self, changes_json: str):
        """Load license change monitoring results"""
        try:
            with open(changes_json, 'r') as f:
                data = json.load(f)

            self.data['changes'] = {
                'total_changes': len(data.get('changes', [])),
                'critical': len([c for c in data.get('changes', []) if c.get('severity') == 'CRITICAL']),
                'high': len([c for c in data.get('changes', []) if c.get('severity') == 'HIGH']),
                'medium': len([c for c in data.get('changes', []) if c.get('severity') == 'MEDIUM']),
                'low': len([c for c in data.get('changes', []) if c.get('severity') == 'LOW']),
                'changes': data.get('changes', [])
            }

            print(f"✅ Loaded change results: {self.data['changes']['total_changes']} changes detected")

            # Generate action items for critical changes
            for change in self.data['changes']['changes']:
                if change.get('severity') == 'CRITICAL':
                    self.data['action_items'].append({
                        'priority': 'CRITICAL',
                        'type': 'License Change',
                        'package': change.get('package'),
                        'action': f"Critical license change: {change.get('old_license')} → {change.get('new_license')}",
                        'deadline': 'Immediate'
                    })

        except Exception as e:
            print(f"⚠️  Warning: Could not load change results: {e}")

    def load_curation_stats(self, stats_json: str):
        """Load smart curation statistics"""
        try:
            with open(stats_json, 'r') as f:
                data = json.load(f)

            self.data['curations'] = data

            print(f"✅ Loaded curation stats: {data.get('total_curations', 0)} suggestions")

            # Generate action items for manual review
            if data.get('manual_review_required', 0) > 0:
                self.data['action_items'].append({
                    'priority': 'MEDIUM',
                    'type': 'Manual Review',
                    'package': f"{data['manual_review_required']} packages",
                    'action': 'Review smart curation suggestions',
                    'deadline': '7 days'
                })

        except Exception as e:
            print(f"⚠️  Warning: Could not load curation stats: {e}")

    def load_sbom_compliance(self, sbom_json: str):
        """Load SBOM compliance results (NTIA minimum elements)"""
        try:
            with open(sbom_json, 'r') as f:
                data = json.load(f)

            self.data['sbom'] = {
                'compliance_score': data.get('compliance_score', 0),
                'ntia_compliant': data.get('ntia_compliant', False),
                'total_packages': data.get('total_packages', 0),
                'missing_author': len(data.get('missing_author', [])),
                'missing_version': len(data.get('missing_version', [])),
                'missing_license': len(data.get('missing_license', [])),
                'missing_identifier': len(data.get('missing_identifier', [])),
                'validation_errors': len(data.get('validation_errors', [])),
                'validation_warnings': len(data.get('validation_warnings', []))
            }

            print(f"✅ Loaded SBOM compliance: {self.data['sbom']['compliance_score']}% score")

            # Generate action items for SBOM compliance issues
            if self.data['sbom']['compliance_score'] < 90:
                priority = 'HIGH' if self.data['sbom']['compliance_score'] < 75 else 'MEDIUM'
                self.data['action_items'].append({
                    'priority': priority,
                    'type': 'SBOM Compliance',
                    'package': f"{self.data['sbom']['missing_license']} packages missing license",
                    'action': 'Improve SBOM metadata to meet NTIA requirements',
                    'deadline': '14 days' if priority == 'MEDIUM' else '7 days'
                })

            if self.data['sbom']['validation_errors'] > 0:
                self.data['action_items'].append({
                    'priority': 'MEDIUM',
                    'type': 'SPDX Validation',
                    'package': f"{self.data['sbom']['validation_errors']} errors",
                    'action': 'Fix SPDX specification validation errors',
                    'deadline': '14 days'
                })

        except Exception as e:
            print(f"⚠️  Warning: Could not load SBOM compliance: {e}")

    def detect_available_reports(self, reports_dir: str):
        """Detect available report files"""
        reports_path = Path(reports_dir)
        if not reports_path.exists():
            return

        # Define report types and their patterns
        report_patterns = {
            'Policy Compliance': 'policy-compliance-report.html',
            'License Changes': 'license-changes-report.html',
            'Alternative Packages': 'alternatives/*.html',
            'Smart Curations': 'manual-review-queue.html',
            'NTIA SBOM Compliance': 'ntia-compliance-report.html',
            'Main AI Curation': 'curation-report-main.html',
            'Conflict Analysis': 'curation-report-conflicts.html',
            'Missing Licenses': 'curation-report-missing-licenses.html',
            'Multi-Layer Comparison': 'license-comparison-report.html',
            'ORT WebApp': 'scan-report-web-app.html',
            'ORT Static HTML': 'scan-report.html',
            'ScanCode Summary': 'scancode-summary.html',
            'Enhanced SPDX': 'bom-enhanced-fixed.spdx.json',
            'SPDX Formats': 'spdx-formats/*.spdx.*',
            'CycloneDX SBOM': 'bom.cyclonedx.json',
        }

        for report_name, pattern in report_patterns.items():
            if '*' in pattern:
                # Glob pattern
                matches = list(reports_path.glob(pattern))
                if matches:
                    self.data['reports'].append({
                        'name': report_name,
                        'files': [str(f.relative_to(reports_path)) for f in matches],
                        'count': len(matches)
                    })
            else:
                # Direct file
                file_path = reports_path / pattern
                if file_path.exists():
                    self.data['reports'].append({
                        'name': report_name,
                        'file': pattern,
                        'count': 1
                    })

        print(f"✅ Detected {len(self.data['reports'])} report types")

    def calculate_overall_metrics(self):
        """Calculate overall compliance metrics"""
        # Overall compliance score (weighted average)
        # Policy: 60%, SBOM: 25%, Changes: 15% (penalty-based)
        policy_score = self.data['policy'].get('compliance_score', 0)
        sbom_score = self.data['sbom'].get('compliance_score', 0) if self.data['sbom'] else 0

        # Weighted base score
        if self.data['sbom']:
            # If SBOM data available: 60% policy + 25% SBOM + 15% buffer for changes
            base_score = (policy_score * 0.60) + (sbom_score * 0.25) + (100 * 0.15)
        else:
            # No SBOM data: use policy score only
            base_score = policy_score

        # Penalty for critical changes
        critical_changes = self.data['changes'].get('critical', 0)
        change_penalty = min(20, critical_changes * 10)  # -10% per critical change, max -20%

        # Penalty for forbidden packages
        forbidden_count = self.data['policy'].get('forbidden', 0)
        forbidden_penalty = min(30, forbidden_count * 15)  # -15% per forbidden, max -30%

        # Penalty for poor SBOM quality
        sbom_penalty = 0
        if self.data['sbom'] and sbom_score < 75:
            sbom_penalty = min(10, (75 - sbom_score) / 5)  # Up to -10% for poor SBOM

        overall_score = max(0, base_score - change_penalty - forbidden_penalty - sbom_penalty)

        # Risk level
        if overall_score >= 90 and critical_changes == 0 and forbidden_count == 0:
            risk_level = 'LOW'
            risk_color = '#4caf50'
        elif overall_score >= 75 and critical_changes == 0:
            risk_level = 'MEDIUM'
            risk_color = '#ff9800'
        elif overall_score >= 60:
            risk_level = 'HIGH'
            risk_color = '#ff5722'
        else:
            risk_level = 'CRITICAL'
            risk_color = '#f44336'

        # Compliance status
        if overall_score >= 95 and critical_changes == 0 and forbidden_count == 0:
            status = 'EXCELLENT'
        elif overall_score >= 85 and critical_changes <= 1 and forbidden_count == 0:
            status = 'GOOD'
        elif overall_score >= 70:
            status = 'ACCEPTABLE'
        elif overall_score >= 50:
            status = 'NEEDS IMPROVEMENT'
        else:
            status = 'CRITICAL'

        self.data['overall'] = {
            'score': overall_score,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'status': status,
            'total_packages': self.data['policy'].get('total', 0),
            'compliant_packages': self.data['policy'].get('approved', 0),
            'action_items_count': len(self.data['action_items']),
            'critical_items': len([a for a in self.data['action_items'] if a['priority'] == 'CRITICAL'])
        }

    def generate_html(self, output_file: str):
        """Generate comprehensive HTML dashboard"""

        overall = self.data['overall']
        policy = self.data['policy']
        changes = self.data['changes']
        curations = self.data['curations']

        html = """<!DOCTYPE html>
<html>
<head>
    <title>License Compliance Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        .header {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #667eea;
            font-size: 3em;
            margin-bottom: 10px;
        }
        .timestamp {
            color: #666;
            font-size: 1.1em;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .card-title {
            font-size: 1.3em;
            color: #333;
            margin-bottom: 15px;
            font-weight: 600;
        }
        .metric-huge {
            font-size: 4em;
            font-weight: bold;
            line-height: 1;
        }
        .metric-large {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }
        .metric-label {
            color: #666;
            font-size: 1.1em;
            margin-top: 10px;
        }
        .score-circle {
            width: 200px;
            height: 200px;
            border-radius: 50%;
            border: 15px solid #e0e0e0;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 20px auto;
            position: relative;
        }
        .risk-low { border-color: #4caf50; }
        .risk-medium { border-color: #ff9800; }
        .risk-high { border-color: #ff5722; }
        .risk-critical { border-color: #f44336; }
        .status-badge {
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.1em;
            margin: 10px 0;
        }
        .status-excellent { background: #4caf50; color: white; }
        .status-good { background: #8bc34a; color: white; }
        .status-acceptable { background: #ff9800; color: white; }
        .status-needs-improvement { background: #ff5722; color: white; }
        .status-critical { background: #f44336; color: white; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin: 20px 0;
        }
        .stat-box {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
            font-size: 0.9em;
        }
        .action-items {
            margin: 20px 0;
        }
        .action-item {
            background: #fff;
            border-left: 5px solid #ccc;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }
        .priority-critical { border-left-color: #f44336; background: #ffebee; }
        .priority-high { border-left-color: #ff9800; background: #fff3e0; }
        .priority-medium { border-left-color: #ffc107; background: #fffde7; }
        .priority-low { border-left-color: #4caf50; background: #f1f8e9; }
        .priority-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
            margin-right: 10px;
        }
        .badge-critical { background: #f44336; color: white; }
        .badge-high { background: #ff9800; color: white; }
        .badge-medium { background: #ffc107; color: #333; }
        .badge-low { background: #4caf50; color: white; }
        .reports-list {
            list-style: none;
        }
        .reports-list li {
            padding: 10px;
            background: #f5f5f5;
            margin: 8px 0;
            border-radius: 6px;
            transition: background 0.2s;
        }
        .reports-list li:hover {
            background: #e0e0e0;
        }
        .reports-list a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        .reports-list a:hover {
            text-decoration: underline;
        }
        .chart-bar {
            background: #e0e0e0;
            height: 30px;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
            position: relative;
        }
        .chart-fill {
            height: 100%;
            transition: width 0.5s;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            color: white;
            font-weight: bold;
        }
        .fill-approved { background: linear-gradient(90deg, #4caf50, #8bc34a); }
        .fill-conditional { background: linear-gradient(90deg, #ff9800, #ffc107); }
        .fill-forbidden { background: linear-gradient(90deg, #f44336, #ff5722); }
        .fill-unknown { background: linear-gradient(90deg, #9e9e9e, #bdbdbd); }
        .icon {
            font-size: 1.5em;
            margin-right: 10px;
        }
        .full-width {
            grid-column: 1 / -1;
        }
        @media (max-width: 768px) {
            h1 { font-size: 2em; }
            .grid { grid-template-columns: 1fr; }
            .stats-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 License Compliance Dashboard</h1>
            <p class="timestamp">Generated: """ + self.data['timestamp'].strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </div>

        <!-- Overall Score -->
        <div class="grid">
            <div class="card">
                <div class="card-title">Overall Compliance Score</div>
                <div class="score-circle risk-""" + overall['risk_level'].lower() + """">
                    <div>
                        <div class="metric-huge" style="color: """ + overall['risk_color'] + """">""" + str(int(overall['score'])) + """<span style="font-size: 0.5em;">%</span></div>
                    </div>
                </div>
                <div style="text-align: center;">
                    <span class="status-badge status-""" + overall['status'].lower().replace(' ', '-') + """">""" + overall['status'] + """</span>
                </div>
            </div>

            <div class="card">
                <div class="card-title">Risk Assessment</div>
                <div class="metric-large" style="color: """ + overall['risk_color'] + """; text-align: center; margin: 40px 0;">
                    <div style="font-size: 3em;">⚠️</div>
                    """ + overall['risk_level'] + """ RISK
                </div>
                <div class="metric-label" style="text-align: center;">
                    Based on compliance score, forbidden packages, and critical changes
                </div>
            </div>

            <div class="card">
                <div class="card-title">Quick Stats</div>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-number">""" + str(overall['total_packages']) + """</div>
                        <div class="stat-label">Total Packages</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">""" + str(overall['compliant_packages']) + """</div>
                        <div class="stat-label">Compliant</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">""" + str(overall['action_items_count']) + """</div>
                        <div class="stat-label">Action Items</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color: #f44336;">""" + str(overall['critical_items']) + """</div>
                        <div class="stat-label">Critical</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Policy Compliance -->
        <div class="grid">
            <div class="card full-width">
                <div class="card-title"><span class="icon">✅</span>Policy Compliance Breakdown</div>
                <div style="margin: 20px 0;">
                    <div>
                        <strong>Approved:</strong> """ + str(policy.get('approved', 0)) + """ packages
                        <div class="chart-bar">
                            <div class="chart-fill fill-approved" style="width: """ + str(int(policy.get('approved', 0) / max(policy.get('total', 1), 1) * 100)) + """%">
                                """ + str(int(policy.get('approved', 0) / max(policy.get('total', 1), 1) * 100)) + """%
                            </div>
                        </div>
                    </div>
                    <div style="margin-top: 15px;">
                        <strong>Conditional:</strong> """ + str(policy.get('conditional', 0)) + """ packages (need approval)
                        <div class="chart-bar">
                            <div class="chart-fill fill-conditional" style="width: """ + str(int(policy.get('conditional', 0) / max(policy.get('total', 1), 1) * 100)) + """%">
                                """ + str(int(policy.get('conditional', 0) / max(policy.get('total', 1), 1) * 100)) + """%
                            </div>
                        </div>
                    </div>
                    <div style="margin-top: 15px;">
                        <strong>Forbidden:</strong> """ + str(policy.get('forbidden', 0)) + """ packages (must replace)
                        <div class="chart-bar">
                            <div class="chart-fill fill-forbidden" style="width: """ + str(int(policy.get('forbidden', 0) / max(policy.get('total', 1), 1) * 100)) + """%">
                                """ + str(int(policy.get('forbidden', 0) / max(policy.get('total', 1), 1) * 100)) + """%
                            </div>
                        </div>
                    </div>
                    <div style="margin-top: 15px;">
                        <strong>Unknown:</strong> """ + str(policy.get('unknown', 0)) + """ packages (need research)
                        <div class="chart-bar">
                            <div class="chart-fill fill-unknown" style="width: """ + str(int(policy.get('unknown', 0) / max(policy.get('total', 1), 1) * 100)) + """%">
                                """ + str(int(policy.get('unknown', 0) / max(policy.get('total', 1), 1) * 100)) + """%
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- License Changes -->
        <div class="grid">
            <div class="card">
                <div class="card-title"><span class="icon">🔄</span>License Changes Detected</div>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-number" style="color: #f44336;">""" + str(changes.get('critical', 0)) + """</div>
                        <div class="stat-label">Critical</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color: #ff9800;">""" + str(changes.get('high', 0)) + """</div>
                        <div class="stat-label">High</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color: #ffc107;">""" + str(changes.get('medium', 0)) + """</div>
                        <div class="stat-label">Medium</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color: #4caf50;">""" + str(changes.get('low', 0)) + """</div>
                        <div class="stat-label">Low</div>
                    </div>
                </div>
                <div class="metric-label" style="text-align: center; margin-top: 15px;">
                    Total Changes: """ + str(changes.get('total_changes', 0)) + """
                </div>
            </div>

            <div class="card">
                <div class="card-title"><span class="icon">🤖</span>Smart Curation Results</div>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-number">""" + str(curations.get('total_curations', 0)) + """</div>
                        <div class="stat-label">Total Suggestions</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color: #4caf50;">""" + str(curations.get('high_confidence', 0)) + """</div>
                        <div class="stat-label">High Confidence</div>
                    </div>
                    <div class="stat-box" style="grid-column: 1 / -1;">
                        <div class="stat-number" style="color: #ff9800;">""" + str(curations.get('manual_review_required', 0)) + """</div>
                        <div class="stat-label">Require Manual Review</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- SBOM Compliance (if available) -->
"""

        sbom = self.data.get('sbom', {})
        if sbom:
            html += f"""
        <div class="grid">
            <div class="card full-width">
                <div class="card-title"><span class="icon">📋</span>SBOM Compliance (NTIA Minimum Elements)</div>
                <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px;">
                    <div class="stat-box">
                        <div class="stat-number" style="color: {'#4caf50' if sbom.get('compliance_score', 0) >= 90 else '#ff9800' if sbom.get('compliance_score', 0) >= 75 else '#f44336'};">{int(sbom.get('compliance_score', 0))}%</div>
                        <div class="stat-label">Compliance Score</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{sbom.get('total_packages', 0)}</div>
                        <div class="stat-label">Total Packages</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color: {'#f44336' if sbom.get('missing_license', 0) > 0 else '#4caf50'};">{sbom.get('missing_license', 0)}</div>
                        <div class="stat-label">Missing License</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color: {'#ff9800' if sbom.get('missing_author', 0) > 0 else '#4caf50'};">{sbom.get('missing_author', 0)}</div>
                        <div class="stat-label">Missing Author</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color: {'#ff9800' if sbom.get('missing_version', 0) > 0 else '#4caf50'};">{sbom.get('missing_version', 0)}</div>
                        <div class="stat-label">Missing Version</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number" style="color: {'#f44336' if sbom.get('validation_errors', 0) > 0 else '#ffc107' if sbom.get('validation_warnings', 0) > 0 else '#4caf50'};">{sbom.get('validation_errors', 0)}</div>
                        <div class="stat-label">SPDX Errors</div>
                    </div>
                </div>
                <div style="margin-top: 20px; padding: 15px; background: {'#e8f5e9' if sbom.get('ntia_compliant', False) and sbom.get('compliance_score', 0) >= 90 else '#fff3e0'}; border-radius: 8px; text-align: center;">
                    <strong style="font-size: 16px; color: {'#2e7d32' if sbom.get('ntia_compliant', False) and sbom.get('compliance_score', 0) >= 90 else '#f57c00'};">
                        {'✅ NTIA Compliant' if sbom.get('ntia_compliant', False) and sbom.get('compliance_score', 0) >= 90 else '⚠️ Needs Improvement'}
                    </strong>
                    <div style="margin-top: 8px; font-size: 13px; color: #666;">
                        {'SBOM meets NTIA minimum elements for software transparency' if sbom.get('ntia_compliant', False) and sbom.get('compliance_score', 0) >= 90 else 'SBOM quality should be improved to meet industry standards'}
                    </div>
                </div>
            </div>
        </div>
"""

        html += """

        <!-- Action Items -->
        <div class="card full-width">
            <div class="card-title"><span class="icon">⚡</span>Priority Action Items</div>
            <div class="action-items">
"""

        # Sort action items by priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        sorted_actions = sorted(self.data['action_items'], key=lambda x: priority_order.get(x['priority'], 4))

        if not sorted_actions:
            html += """
                <div class="action-item priority-low">
                    <strong>🎉 No action items!</strong> - All packages are compliant.
                </div>
"""
        else:
            for action in sorted_actions[:10]:  # Show top 10
                priority_class = f"priority-{action['priority'].lower()}"
                badge_class = f"badge-{action['priority'].lower()}"

                html += f"""
                <div class="action-item {priority_class}">
                    <span class="priority-badge {badge_class}">{action['priority']}</span>
                    <strong>{action['type']}:</strong> {action['package']}<br>
                    <div style="margin-top: 8px;">
                        📋 <strong>Action:</strong> {action['action']}<br>
                        ⏰ <strong>Deadline:</strong> {action['deadline']}
                    </div>
                </div>
"""

            if len(sorted_actions) > 10:
                html += f"""
                <div style="text-align: center; margin-top: 15px; color: #666;">
                    ... and {len(sorted_actions) - 10} more action items
                </div>
"""

        html += """
            </div>
        </div>

        <!-- Available Reports -->
        <div class="card full-width">
            <div class="card-title"><span class="icon">📄</span>Available Reports</div>
            <ul class="reports-list">
"""

        if not self.data['reports']:
            html += """
                <li>No reports detected. Run the full workflow to generate reports.</li>
"""
        else:
            for report in self.data['reports']:
                if 'file' in report:
                    html += f"""
                <li>
                    <a href="{report['file']}" target="_blank">📊 {report['name']}</a>
                </li>
"""
                elif 'files' in report:
                    html += f"""
                <li>
                    📊 {report['name']} ({report['count']} files)
"""
                    for file in report['files'][:5]:  # Show max 5
                        html += f"""
                    <br>&nbsp;&nbsp;&nbsp;&nbsp;↳ <a href="{file}" target="_blank">{Path(file).name}</a>
"""
                    if report['count'] > 5:
                        html += f"""
                    <br>&nbsp;&nbsp;&nbsp;&nbsp;... and {report['count'] - 5} more
"""
                    html += """
                </li>
"""

        html += """
            </ul>
        </div>

        <!-- Footer -->
        <div class="card full-width" style="text-align: center; margin-top: 20px;">
            <p style="color: #666;">
                Generated by <strong>License Compliance Dashboard</strong><br>
                Advanced License Curation Workflow System<br>
                <small>Last updated: """ + self.data['timestamp'].strftime("%Y-%m-%d %H:%M:%S UTC") + """</small>
            </p>
        </div>
    </div>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ Generated compliance dashboard: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Compliance Dashboard - Generate unified license compliance dashboard'
    )
    parser.add_argument('--policy-json', help='Policy compliance results JSON file')
    parser.add_argument('--changes-json', help='License changes results JSON file')
    parser.add_argument('--curation-stats', help='Smart curation statistics JSON file')
    parser.add_argument('--sbom-json', help='SBOM compliance (NTIA) results JSON file')
    parser.add_argument('--reports-dir', default='.',
                       help='Directory to scan for available reports')
    parser.add_argument('--output', default='compliance-dashboard.html',
                       help='Output HTML file')

    args = parser.parse_args()

    print("📊 Compliance Dashboard Generator")
    print("=" * 60)

    # Initialize dashboard
    dashboard = ComplianceDashboard()

    # Load data sources
    if args.policy_json:
        print("\n📊 Loading policy compliance results...")
        dashboard.load_policy_results(args.policy_json)

    if args.changes_json:
        print("\n🔄 Loading license change results...")
        dashboard.load_change_results(args.changes_json)

    if args.curation_stats:
        print("\n🤖 Loading smart curation statistics...")
        dashboard.load_curation_stats(args.curation_stats)

    if args.sbom_json:
        print("\n📋 Loading SBOM compliance results...")
        dashboard.load_sbom_compliance(args.sbom_json)

    # Detect available reports
    print("\n📄 Detecting available reports...")
    dashboard.detect_available_reports(args.reports_dir)

    # Calculate overall metrics
    print("\n📈 Calculating overall compliance metrics...")
    dashboard.calculate_overall_metrics()

    # Generate dashboard
    print("\n🎨 Generating HTML dashboard...")
    dashboard.generate_html(args.output)

    # Summary
    overall = dashboard.data['overall']
    print("\n" + "=" * 60)
    print("✅ Compliance Dashboard generated successfully!")
    print(f"\n📊 Overall Compliance Score: {int(overall['score'])}%")
    print(f"⚠️  Risk Level: {overall['risk_level']}")
    print(f"📈 Status: {overall['status']}")
    print(f"🚨 Critical Action Items: {overall['critical_items']}")
    print(f"\n📄 Dashboard: {args.output}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
