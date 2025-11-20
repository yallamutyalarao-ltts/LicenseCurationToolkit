#!/usr/bin/env python3
"""Generate landing page for GitHub Pages deployment"""

import sys
import os
from pathlib import Path

def generate_landing_page(public_dir='public'):
    """Generate index.html landing page for ORT reports"""

    public_path = Path(public_dir)

    # Detect available files
    webapp_file = ''
    static_html = ''
    ai_main_report = ''
    ai_conflict_report = ''
    ai_missing_licenses = ''
    ai_resolution_report = ''
    license_comparison = ''
    cyclonedx = ''
    spdx_enhanced = ''
    spdx_original = ''
    uncertain_report = ''
    scancode_html = ''
    scancode_yaml = ''
    pypi_html_report = ''
    compliance_dashboard = ''
    policy_compliance = ''
    license_changes = ''
    manual_review_queue = ''
    ntia_compliance_report = ''

    # Find files
    for file in public_path.glob('*web-app*.html'):
        webapp_file = file.name
        break

    # Find static HTML report (scan-report.html)
    if (public_path / 'scan-report.html').exists():
        static_html = 'scan-report.html'

    if (public_path / 'curation-report-main.html').exists():
        ai_main_report = 'curation-report-main.html'

    if (public_path / 'curation-report-missing-licenses.html').exists():
        ai_missing_licenses = 'curation-report-missing-licenses.html'

    if (public_path / 'curation-report-conflicts.html').exists():
        ai_conflict_report = 'curation-report-conflicts.html'

    if (public_path / 'license-comparison.html').exists():
        license_comparison = 'license-comparison.html'

    if (public_path / 'ai-multilayer-resolution.html').exists():
        ai_resolution_report = 'ai-multilayer-resolution.html'

    if (public_path / 'bom.cyclonedx.json').exists():
        cyclonedx = 'bom.cyclonedx.json'

    if (public_path / 'bom-enhanced.spdx.json').exists():
        spdx_enhanced = 'bom-enhanced.spdx.json'

    if (public_path / 'bom.spdx.yml').exists():
        spdx_original = 'bom.spdx.yml'

    if (public_path / 'uncertain-packages-report.md').exists():
        uncertain_report = 'uncertain-packages-report.md'

    if (public_path / 'scancode-summary.html').exists():
        scancode_html = 'scancode-summary.html'

    if (public_path / 'scancode-summary.yml').exists():
        scancode_yaml = 'scancode-summary.yml'

    if (public_path / 'pypi-licenses-report.html').exists():
        pypi_html_report = 'pypi-licenses-report.html'

    # Advanced Policy Management Reports
    if (public_path / 'compliance-dashboard.html').exists():
        compliance_dashboard = 'compliance-dashboard.html'

    if (public_path / 'policy-compliance-report.html').exists():
        policy_compliance = 'policy-compliance-report.html'

    if (public_path / 'license-changes-report.html').exists():
        license_changes = 'license-changes-report.html'

    if (public_path / 'manual-review-queue.html').exists():
        manual_review_queue = 'manual-review-queue.html'

    # SBOM and SPDX Compliance Reports
    if (public_path / 'ntia-compliance-report.html').exists():
        ntia_compliance_report = 'ntia-compliance-report.html'

    # Check for SPDX formats directory
    spdx_formats_dir = public_path / 'spdx-formats'
    spdx_formats_available = []
    if spdx_formats_dir.exists():
        if (spdx_formats_dir / 'bom.spdx.json').exists():
            spdx_formats_available.append({'format': 'JSON', 'file': 'spdx-formats/bom.spdx.json', 'desc': 'API & programmatic'})
        if (spdx_formats_dir / 'bom.spdx.yml').exists():
            spdx_formats_available.append({'format': 'YAML', 'file': 'spdx-formats/bom.spdx.yml', 'desc': 'Version control'})
        if (spdx_formats_dir / 'bom.spdx.tv').exists():
            spdx_formats_available.append({'format': 'Tag-Value', 'file': 'spdx-formats/bom.spdx.tv', 'desc': 'Human-readable'})
        if (spdx_formats_dir / 'bom.spdx.rdf').exists():
            spdx_formats_available.append({'format': 'RDF', 'file': 'spdx-formats/bom.spdx.rdf', 'desc': 'Semantic web'})

    # Find individual ScanCode package reports
    scancode_reports_dir = public_path / 'scancode-reports'
    scancode_package_reports = []
    if scancode_reports_dir.exists():
        for html_file in sorted(scancode_reports_dir.glob('*.html')):
            scancode_package_reports.append({
                'name': html_file.stem,
                'html': f'scancode-reports/{html_file.name}',
                'json': f'scancode-reports/{html_file.stem}.json',
                'yaml': f'scancode-reports/{html_file.stem}.yml'
            })

    print(f"✅ Detected files:")
    print(f"  WebApp: {webapp_file or 'N/A'}")
    print(f"  Static HTML: {static_html or 'N/A'}")
    print(f"  AI Main Report: {ai_main_report or 'N/A'}")
    print(f"  AI Conflict Report: {ai_conflict_report or 'N/A'}")
    print(f"  AI Missing Licenses: {ai_missing_licenses or 'N/A'}")
    print(f"  AI Resolution Report: {ai_resolution_report or 'N/A'}")
    print(f"  License Comparison: {license_comparison or 'N/A'}")
    print(f"  CycloneDX: {cyclonedx or 'N/A'}")
    print(f"  SPDX Enhanced: {spdx_enhanced or 'N/A'}")
    print(f"  SPDX Original: {spdx_original or 'N/A'}")
    print(f"  Uncertain Report: {uncertain_report or 'N/A'}")
    print(f"  ScanCode HTML: {scancode_html or 'N/A'}")
    print(f"  ScanCode YAML: {scancode_yaml or 'N/A'}")
    print(f"  PyPI HTML Report: {pypi_html_report or 'N/A'}")
    print(f"  ScanCode Package Reports: {len(scancode_package_reports)} packages")
    print(f"  Compliance Dashboard: {compliance_dashboard or 'N/A'}")
    print(f"  Policy Compliance: {policy_compliance or 'N/A'}")
    print(f"  License Changes: {license_changes or 'N/A'}")
    print(f"  Manual Review Queue: {manual_review_queue or 'N/A'}")

    # Generate HTML
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Enhanced ORT Analysis Reports</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, rgba(102,126,234,0.9), rgba(118,75,162,0.9)),
                  url('background.jpg') no-repeat center center fixed;
      background-size: cover;
      min-height: 100vh;
      padding: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .container {
      background: white;
      border-radius: 16px;
      padding: 40px;
      max-width: 1000px;
      width: 100%;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    h1 {
      color: #2d3748;
      margin-bottom: 10px;
      font-size: 2.5rem;
    }
    .subtitle {
      color: #718096;
      margin-bottom: 30px;
      font-size: 1.1rem;
    }
    .badge {
      display: inline-block;
      background: linear-gradient(135deg, #667eea, #764ba2);
      color: white;
      padding: 6px 16px;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 600;
      margin-left: 8px;
    }
    .report-grid {
      display: grid;
      gap: 16px;
      margin-top: 30px;
    }
    .report-card {
      background: #f7fafc;
      border: 2px solid #e2e8f0;
      border-radius: 12px;
      padding: 24px;
      transition: all 0.3s;
      text-decoration: none;
      display: block;
    }
    .report-card:hover {
      border-color: #667eea;
      box-shadow: 0 4px 12px rgba(102,126,234,0.2);
      transform: translateY(-2px);
    }
    .highlight {
      background: linear-gradient(135deg, #667eea, #764ba2);
      border: none;
    }
    .highlight .report-title,
    .highlight .report-desc {
      color: white;
    }
    .report-icon {
      font-size: 2rem;
      margin-bottom: 12px;
    }
    .report-title {
      color: #2d3748;
      font-size: 1.3rem;
      font-weight: 600;
      margin-bottom: 8px;
    }
    .report-desc {
      color: #718096;
      font-size: 0.95rem;
      line-height: 1.5;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>🔍 Enhanced ORT Analysis Reports</h1>
    <p class="subtitle">Multi-Tool License Compliance Analysis <span class="badge">ENHANCED</span></p>

    <div class="report-grid">
'''

    # Add Compliance Dashboard (MOST PROMINENT)
    if compliance_dashboard:
        html += f'''
      <a href="{compliance_dashboard}" class="report-card highlight">
        <div class="report-icon">📊</div>
        <div class="report-title">Compliance Dashboard <span class="badge">EXECUTIVE SUMMARY</span></div>
        <div class="report-desc">Unified view of all compliance metrics - policy status, license changes, risk assessment, and action items</div>
      </a>
'''

    # Add Policy Compliance Report
    if policy_compliance:
        html += f'''
      <a href="{policy_compliance}" class="report-card highlight">
        <div class="report-icon">✅</div>
        <div class="report-title">Policy Compliance Report <span class="badge">POLICY CHECK</span></div>
        <div class="report-desc">Package compliance against company license policy - approved, conditional, forbidden, unknown packages</div>
      </a>
'''

    # Add License Changes Report
    if license_changes:
        html += f'''
      <a href="{license_changes}" class="report-card highlight">
        <div class="report-icon">🔄</div>
        <div class="report-title">License Change Alerts <span class="badge">MONITORING</span></div>
        <div class="report-desc">Historical license tracking with severity assessment and recommended actions for detected changes</div>
      </a>
'''

    # Add Manual Review Queue (Smart Curation)
    if manual_review_queue:
        html += f'''
      <a href="{manual_review_queue}" class="report-card highlight">
        <div class="report-icon">🔍</div>
        <div class="report-title">Smart Curation Review Queue <span class="badge">REQUIRES REVIEW</span></div>
        <div class="report-desc">Packages requiring manual verification with confidence scores and evidence from multiple sources</div>
      </a>
'''

    # Add NTIA SBOM Compliance Report
    if ntia_compliance_report:
        html += f'''
      <a href="{ntia_compliance_report}" class="report-card highlight">
        <div class="report-icon">📋</div>
        <div class="report-title">SBOM Compliance Report <span class="badge">NTIA</span></div>
        <div class="report-desc">SBOM validation against NTIA minimum elements - compliance score, missing metadata, and quality metrics</div>
      </a>
'''

    # Add AI main curation report
    if ai_main_report:
        html += f'''
      <a href="{ai_main_report}" class="report-card highlight">
        <div class="report-icon">🤖</div>
        <div class="report-title">AI Curation Report <span class="badge">PRIMARY</span></div>
        <div class="report-desc">Comprehensive AI-powered ORT analysis and compliance recommendations</div>
      </a>
'''

    # Add AI conflict analysis report
    if ai_conflict_report:
        html += f'''
      <a href="{ai_conflict_report}" class="report-card highlight">
        <div class="report-icon">⚠️</div>
        <div class="report-title">License Conflict Analysis <span class="badge">ENHANCED</span></div>
        <div class="report-desc">Multi-tool conflict resolution with ORT + ScanCode + AI recommendations</div>
      </a>
'''

    # Add AI missing licenses report
    if ai_missing_licenses:
        html += f'''
      <a href="{ai_missing_licenses}" class="report-card highlight">
        <div class="report-icon">🔍</div>
        <div class="report-title">Missing Licenses Analysis <span class="badge">AI RESEARCH</span></div>
        <div class="report-desc">AI-powered license suggestions for packages with missing or blank licenses</div>
      </a>
'''

    # Add Multi-Layer License Comparison
    if license_comparison:
        html += f'''
      <a href="{license_comparison}" class="report-card highlight">
        <div class="report-icon">📊</div>
        <div class="report-title">Multi-Layer License Comparison <span class="badge">ALL SOURCES</span></div>
        <div class="report-desc">Comprehensive license comparison from ORT, PyPI API, and ScanCode with conflict detection</div>
      </a>
'''

    # Add AI Multi-Layer Resolution Report
    if ai_resolution_report:
        html += f'''
      <a href="{ai_resolution_report}" class="report-card highlight">
        <div class="report-icon">🤖</div>
        <div class="report-title">AI Multi-Layer Resolution <span class="badge">SMART ANALYSIS</span></div>
        <div class="report-desc">AI-powered intelligent resolution for conflicts and missing licenses with actionable recommendations</div>
      </a>
'''

    # Add PyPI HTML report
    if pypi_html_report:
        html += f'''
      <a href="{pypi_html_report}" class="report-card highlight">
        <div class="report-icon">🌐</div>
        <div class="report-title">PyPI License Fetch Report <span class="badge">FAST API</span></div>
        <div class="report-desc">Licenses retrieved from PyPI API - reduces ScanCode workload significantly</div>
      </a>
'''

    # Add ScanCode HTML report
    if scancode_html:
        html += f'''
      <a href="{scancode_html}" class="report-card highlight">
        <div class="report-icon">🔬</div>
        <div class="report-title">ScanCode Analysis Report <span class="badge">DEEP SCAN</span></div>
        <div class="report-desc">File-level license detection and copyright analysis</div>
      </a>
'''

    # Add ORT WebApp
    if webapp_file:
        html += f'''
      <a href="{webapp_file}" class="report-card">
        <div class="report-icon">🌐</div>
        <div class="report-title">ORT WebApp Report</div>
        <div class="report-desc">Interactive dependency tree and license visualization</div>
      </a>
'''

    # Add ORT Static HTML
    if static_html:
        html += f'''
      <a href="{static_html}" class="report-card">
        <div class="report-icon">📊</div>
        <div class="report-title">ORT Static HTML Report</div>
        <div class="report-desc">Traditional static compliance report with all license details</div>
      </a>
'''

    # Add ScanCode YAML report
    if scancode_yaml:
        html += f'''
      <a href="{scancode_yaml}" class="report-card">
        <div class="report-icon">📄</div>
        <div class="report-title">ScanCode YAML Summary</div>
        <div class="report-desc">Machine-readable ScanCode analysis results</div>
      </a>
'''

    # Add enhanced SPDX
    if spdx_enhanced:
        html += f'''
      <a href="{spdx_enhanced}" class="report-card">
        <div class="report-icon">✨</div>
        <div class="report-title">Enhanced SPDX Document</div>
        <div class="report-desc">SPDX enhanced with ScanCode license detections</div>
      </a>
'''

    # Add CycloneDX
    if cyclonedx:
        html += f'''
      <a href="{cyclonedx}" class="report-card">
        <div class="report-icon">📦</div>
        <div class="report-title">CycloneDX SBOM</div>
        <div class="report-desc">Software Bill of Materials in CycloneDX format</div>
      </a>
'''

    # Add SPDX Formats Section (multiple formats available)
    if spdx_formats_available:
        html += '''
      <div class="report-card highlight" style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);">
        <div class="report-icon">📄</div>
        <div class="report-title">SPDX Formats <span class="badge">MULTI-FORMAT</span></div>
        <div class="report-desc">SBOM available in multiple SPDX formats for different use cases:</div>
        <div style="margin-top: 12px; display: flex; flex-wrap: wrap; gap: 8px;">
'''
        for fmt in spdx_formats_available:
            html += f'''
          <a href="{fmt['file']}" style="background: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; color: #1976d2; font-weight: 600; font-size: 13px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: all 0.2s;" onmouseover="this.style.boxShadow='0 4px 8px rgba(0,0,0,0.15)'; this.style.transform='translateY(-2px)';" onmouseout="this.style.boxShadow='0 2px 4px rgba(0,0,0,0.1)'; this.style.transform='translateY(0)';">
            {fmt['format']} <span style="color: #666; font-weight: normal; font-size: 11px;">({fmt['desc']})</span>
          </a>
'''
        html += '''
        </div>
      </div>
'''

    # Add original SPDX if no enhanced version
    if spdx_original and not spdx_enhanced:
        html += f'''
      <a href="{spdx_original}" class="report-card">
        <div class="report-icon">📋</div>
        <div class="report-title">SPDX Document</div>
        <div class="report-desc">Software Package Data Exchange standard format</div>
      </a>
'''

    # Add uncertain packages report
    if uncertain_report:
        html += f'''
      <a href="{uncertain_report}" class="report-card">
        <div class="report-icon">⚠️</div>
        <div class="report-title">Uncertain Packages Report</div>
        <div class="report-desc">Packages requiring manual license review</div>
      </a>
'''

    # Close main report grid
    html += '''
    </div>
'''

    # Add individual ScanCode package reports section
    if scancode_package_reports:
        html += '''
    <h2 style="margin-top: 40px; margin-bottom: 20px; color: #2d3748;">📦 Individual Package ScanCode Reports</h2>
    <div style="background: #f7fafc; border: 2px solid #e2e8f0; border-radius: 8px; padding: 20px;">
'''
        for report in scancode_package_reports:
            html += f'''
      <div style="padding: 12px 0; border-bottom: 1px solid #e2e8f0;">
        <div style="font-weight: 600; color: #2d3748; margin-bottom: 8px;">{report['name']}</div>
        <div style="display: flex; gap: 12px;">
          <a href="{report['html']}" style="color: #667eea; text-decoration: none; font-size: 0.9rem;">📄 HTML Report</a>
          <a href="{report['json']}" style="color: #667eea; text-decoration: none; font-size: 0.9rem;">📋 JSON</a>
          <a href="{report['yaml']}" style="color: #667eea; text-decoration: none; font-size: 0.9rem;">📝 YAML</a>
        </div>
      </div>
'''
        html += '''
    </div>
'''

    # Close HTML
    html += '''
  </div>
</body>
</html>
'''

    # Write index.html
    index_path = public_path / 'index.html'
    with open(index_path, 'w') as f:
        f.write(html)

    print(f"✅ Landing page generated: {index_path}")

if __name__ == '__main__':
    public_dir = sys.argv[1] if len(sys.argv) > 1 else 'public'
    generate_landing_page(public_dir)
