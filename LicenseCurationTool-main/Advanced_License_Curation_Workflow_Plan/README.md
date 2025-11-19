# Advanced License Curation Workflow

> Comprehensive solution for managing missing, conflicted, and company-non-compliant licenses with automated policy enforcement, change monitoring, and alternative package suggestions.

[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Solution Architecture](#solution-architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Workflow Integration](#workflow-integration)
- [Reports Generated](#reports-generated)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This system provides a **complete solution** for handling complex license curation scenarios that standard ORT workflows cannot address:

1. **Missing Licenses** - Packages with NOASSERTION/UNKNOWN/blank licenses
2. **Conflicted Licenses** - Different tools report different licenses
3. **Company Non-Compliant Licenses** - Forbidden/restricted licenses (GPL, SSPL, etc.)
4. **Suddenly Changed Licenses** - Detection and alert system
5. **Alternative Package Recommendations** - Automatic suggestions when conflicts arise

---

## 🚨 Problem Statement

### What We're Solving

**Scenario 1: Missing Licenses**
- Package has no declared license (NOASSERTION)
- Standard tools can't determine licensing
- Legal team needs guidance before approval

**Scenario 2: Conflicted Licenses**
- ORT says "MIT", ScanCode says "GPL-3.0", PyPI says "Apache-2.0"
- Which one is correct?
- How to resolve conflicts systematically?

**Scenario 3: Company Non-Compliant Licenses**
- Package uses GPL-3.0, but company policy forbids copyleft in products
- Need to find alternative packages with compatible licenses
- Requires approval workflow for exceptions

**Scenario 4: Suddenly Changed Licenses**
- Package version 1.0 was MIT
- Package version 2.0 changed to AGPL-3.0
- Critical risk: Existing deployments now non-compliant

---

## 🏗️ Solution Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    Source Code / Dependencies                  │
└────────────────────┬───────────────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │   1. ORT Analysis     │
         └───────────┬───────────┘
                     │
         ┌───────────▼────────────────┐
         │  2. Policy Checker         │ ◄─── Company Policy Database
         │  (policy_checker.py)       │      (company-policy.yml)
         └───────────┬────────────────┘
                     │
         ┌───────────▼────────────────────────────┐
         │  Decision Tree:                        │
         │  ┌──────────────────────────────────┐  │
         │  │ ✅ Approved?                     │  │
         │  │   → Generate Curation            │  │
         │  ├──────────────────────────────────┤  │
         │  │ ❌ Forbidden?                    │  │
         │  │   → Find Alternatives            │───┐
         │  ├──────────────────────────────────┤  │
         │  │ ❓ Unknown?                      │  │
         │  │   → Fetch PyPI/NPM → ScanCode    │  │
         │  ├──────────────────────────────────┤  │
         │  │ ⚠️  Conditional?                  │  │
         │  │   → Request Approval             │  │
         │  ├──────────────────────────────────┤  │
         │  │ 🔄 Changed?                      │  │
         │  │   → Alert + Severity Assessment  │  │
         │  └──────────────────────────────────┘  │
         └────────────────────────────────────────┘
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
     ┌───────────▼──────────┐     ┌───────────▼──────────────┐
     │ 3. License Change    │     │ 4. Alternative Package   │
     │    Monitor           │     │    Finder                │
     │ (license_change_     │     │ (alternative_package_    │
     │  monitor.py)         │     │  finder.py)              │
     └───────────┬──────────┘     └───────────┬──────────────┘
                 │                             │
                 └──────────────┬──────────────┘
                                │
                 ┌──────────────▼──────────────┐
                 │  5. Smart Curation Engine   │
                 │  (smart_curation_engine.py) │
                 │  Combines all decisions     │
                 └──────────────┬──────────────┘
                                │
                 ┌──────────────▼──────────────┐
                 │  6. Compliance Dashboard    │
                 │  (compliance_dashboard.py)  │
                 │  Unified HTML Report        │
                 └─────────────────────────────┘
```

---

## ✨ Features

### 🔒 **Policy-Based License Management**
- Define company-specific approved/conditional/forbidden licenses
- Automatic policy enforcement during CI/CD
- License compatibility matrix
- Approval workflows for conditional licenses

### 🔍 **License Change Detection**
- Historical tracking database (`.ort/license-history.json`)
- Automatic severity assessment (CRITICAL/HIGH/MEDIUM/LOW)
- Alert generation for sudden changes
- Permissive-to-Copyleft detection (e.g., MIT → GPL)

### 🔄 **Alternative Package Finder**
- Automatic search for compliant alternatives
- Scoring based on:
  - License compatibility (40%)
  - Popularity/downloads (25%)
  - Maintenance status (20%)
  - Documentation quality (10%)
  - Security track record (5%)
- Side-by-side comparison reports

### 🤖 **Smart Decision Engine**
- Multi-tool conflict resolution
- Evidence-based curation suggestions
- Confidence scoring
- Manual review workflow integration

### 📊 **Comprehensive Reporting**
- Policy compliance report (HTML)
- License change alerts (HTML)
- Alternative packages report (HTML)
- Compliance dashboard (unified view)
- JSON exports for automation

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+ with pip
python --version

# ORT installed (for initial scans)
ort --version

# Required Python packages
pip install pyyaml requests
```

### 5-Minute Setup

```bash
# 1. Clone/download to your repository
cd your-project-root
cp -r Advanced_License_Curation_Workflow .

# 2. Configure company policy
cd Advanced_License_Curation_Workflow
nano config/company-policy.yml  # Edit approved/forbidden licenses

# 3. Run initial license scan
cd ..
ort analyze -i . -o ort-results/analyzer

# 4. Check policy compliance
python Advanced_License_Curation_Workflow/scripts/policy_checker.py \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --output policy-compliance-report.html

# 5. Open report
# Windows: start policy-compliance-report.html
# Linux: xdg-open policy-compliance-report.html
# Mac: open policy-compliance-report.html
```

---

## 📦 Installation

### Step 1: Copy Scripts to Your Repository

```bash
# Copy entire Advanced_License_Curation_Workflow folder to your repository root
cp -r Advanced_License_Curation_Workflow /path/to/your/repo/
```

### Step 2: Install Python Dependencies

```bash
pip install -r Advanced_License_Curation_Workflow/requirements.txt
```

Create `requirements.txt`:
```txt
pyyaml>=6.0
requests>=2.28.0
```

### Step 3: Configure Company Policy

Edit `config/company-policy.yml`:

```yaml
company_license_policy:
  company_name: "Your Company Name"

  approved_licenses:
    permissive:
      licenses:
        - "MIT"
        - "Apache-2.0"
        - "BSD-3-Clause"

  forbidden_licenses:
    proprietary_restricted:
      licenses:
        - "SSPL-1.0"
        - "GPL-3.0-only"  # Example: if company forbids GPL
```

### Step 4: Initialize License History Tracking

```bash
python scripts/license_change_monitor.py --init \
  --ort-results ort-results/analyzer/analyzer-result.yml
```

---

## 🎮 Usage

### 1. Policy Compliance Check

**Check all packages against company policy:**

```bash
python scripts/policy_checker.py \
  --policy config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --output policy-compliance-report.html \
  --json policy-results.json
```

**Output:**
- HTML report with compliance status (green/yellow/red)
- JSON export for automation
- Exit code 1 if forbidden packages found

**Example Output:**
```
✅ Analyzed 50 packages
   ✅ Approved:    42
   ⚠️  Conditional: 5
   ❌ Forbidden:   2
   ❓ Unknown:     1
   📈 Compliance Score: 84%
```

---

### 2. Find Alternative Packages

**When forbidden license detected:**

```bash
python scripts/alternative_package_finder.py \
  --package "pycutest" \
  --type "PyPI" \
  --forbidden-license "GPL-3.0-or-later" \
  --policy config/company-policy.yml \
  --output alternatives-pycutest.html \
  --max-results 5
```

**Output:**
- HTML report with top 5 alternatives
- Ranked by compatibility score
- Side-by-side comparison
- Direct links to package registries

**Example Output:**
```
✅ Found 5 alternatives

Top 3 recommendations:
  1. cutest-alternative (MIT) - Score: 0.92
  2. optimization-lib (Apache-2.0) - Score: 0.88
  3. solver-toolkit (BSD-3-Clause) - Score: 0.85
```

---

### 3. License Change Monitoring

**Initialize tracking (first time):**

```bash
python scripts/license_change_monitor.py --init \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --history .ort/license-history.json
```

**Check for changes (subsequent runs):**

```bash
python scripts/license_change_monitor.py --check \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --policy config/company-policy.yml \
  --output license-changes-report.html \
  --fail-on-critical
```

**Output:**
- HTML alert report for changed licenses
- Severity assessment (CRITICAL/HIGH/MEDIUM/LOW)
- Recommended actions for each change
- Fails build if critical changes detected (with `--fail-on-critical`)

**Example Output:**
```
📊 Results:
   Total changes detected: 3
   ⛔ Critical: 1
   ⚠️  High:     1
   📋 Medium:   1
   ℹ️  Low:      0

❌ CRITICAL LICENSE CHANGES DETECTED!
   requests 2.28.0: MIT → GPL-3.0-only
```

---

### 4. Complete Workflow

**Run all checks in sequence:**

```bash
#!/bin/bash
# complete-license-check.sh

set -e

echo "🔍 Running complete license curation workflow..."

# Step 1: ORT Analysis
echo "1. Running ORT analysis..."
ort analyze -i . -o ort-results/analyzer

# Step 2: Policy Check
echo "2. Checking policy compliance..."
python scripts/policy_checker.py \
  --policy config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --output policy-compliance-report.html

# Step 3: Check for license changes
echo "3. Checking for license changes..."
python scripts/license_change_monitor.py --check \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --policy config/company-policy.yml \
  --output license-changes-report.html

# Step 4: Find alternatives for forbidden packages
echo "4. Finding alternatives for forbidden packages..."
# Extract forbidden packages and find alternatives
# (custom logic based on policy-results.json)

echo "✅ Complete! Open reports:"
echo "  - policy-compliance-report.html"
echo "  - license-changes-report.html"
```

---

## ⚙️ Configuration

### Company Policy Database

**Location:** `config/company-policy.yml`

**Key Sections:**

#### 1. Approved Licenses

```yaml
approved_licenses:
  permissive:
    licenses:
      - "MIT"
      - "Apache-2.0"
    auto_approve: true
    conditions: []
```

#### 2. Conditional Licenses

```yaml
conditional_licenses:
  strong_copyleft:
    licenses:
      - "GPL-3.0-only"
    approval_required: true
    approvers:
      - "legal@company.com"
    conditions:
      - "Requires legal team approval"
```

#### 3. Forbidden Licenses

```yaml
forbidden_licenses:
  proprietary_restricted:
    licenses:
      - "SSPL-1.0"
      - "Elastic-2.0"
    reason: "Incompatible with company business model"
    action: "reject"
```

#### 4. License Compatibility Matrix

```yaml
license_compatibility:
  - combination: "MIT AND Apache-2.0"
    compatible: true
  - combination: "Apache-2.0 AND GPL-2.0-only"
    compatible: false
    reason: "Apache patent clause incompatible with GPL-2.0"
```

#### 5. Alternative Package Preferences

```yaml
alternative_package_preferences:
  prefer_licenses:
    - "MIT"
    - "Apache-2.0"

  min_monthly_downloads: 1000
  min_github_stars: 100

  ranking_weights:
    license_compatibility: 0.40
    popularity: 0.25
    maintenance: 0.20
```

---

## 🔄 Workflow Integration

### GitHub Actions Integration

Create `.github/workflows/license-compliance.yml`:

```yaml
name: License Compliance Check

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  license-check:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install pyyaml requests

      - name: Install ORT
        run: |
          ORT_VERSION="70.0.1"
          wget https://github.com/oss-review-toolkit/ort/releases/download/${ORT_VERSION}/ort-${ORT_VERSION}.tgz
          tar -xzf ort-${ORT_VERSION}.tgz
          echo "${PWD}/ort-${ORT_VERSION}/bin" >> $GITHUB_PATH

      - name: Run ORT Analysis
        run: |
          ort analyze -i . -o ort-results/analyzer

      - name: Check Policy Compliance
        run: |
          python Advanced_License_Curation_Workflow/scripts/policy_checker.py \
            --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
            --ort-results ort-results/analyzer/analyzer-result.yml \
            --output policy-compliance-report.html \
            --json policy-results.json

      - name: Check License Changes
        run: |
          python Advanced_License_Curation_Workflow/scripts/license_change_monitor.py --check \
            --ort-results ort-results/analyzer/analyzer-result.yml \
            --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
            --output license-changes-report.html \
            --fail-on-critical

      - name: Upload Reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: license-compliance-reports
          path: |
            policy-compliance-report.html
            license-changes-report.html
            policy-results.json
          retention-days: 30

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('policy-results.json'));

            const comment = `## 📋 License Compliance Report

            **Compliance Score:** ${results.summary.compliance_score}%

            - ✅ Approved: ${results.summary.approved}
            - ⚠️ Conditional: ${results.summary.conditional}
            - ❌ Forbidden: ${results.summary.forbidden}
            - ❓ Unknown: ${results.summary.unknown}

            [View Full Report](${process.env.GITHUB_SERVER_URL}/${process.env.GITHUB_REPOSITORY}/actions/runs/${process.env.GITHUB_RUN_ID})
            `;

            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: comment
            });
```

---

## 📊 Reports Generated

### 1. Policy Compliance Report

**File:** `policy-compliance-report.html`

**Features:**
- Compliance score (0-100%)
- Package-by-package status
- Risk level indicators
- Required approvals
- Conditions for conditional licenses

**Visual Indicators:**
- 🟢 Green: Approved licenses
- 🟡 Yellow: Conditional/approval required
- 🔴 Red: Forbidden licenses
- ⚪ Gray: Unknown licenses

---

### 2. License Change Alert

**File:** `license-changes-report.html`

**Features:**
- Detected changes since last scan
- Severity assessment
- Risk analysis
- Step-by-step recommended actions
- Historical timeline

---

### 3. Alternative Packages Report

**File:** `alternatives-{package}.html`

**Features:**
- Top alternatives ranked by score
- License comparison
- Popularity metrics (downloads, stars)
- Maintenance status
- Direct links to verify

---

## 📝 Best Practices

### 1. Policy Configuration

- **Start Conservative:** Begin with strict policy, loosen as needed
- **Document Decisions:** Add comments explaining why licenses are forbidden
- **Version Control:** Commit `company-policy.yml` to git
- **Regular Review:** Update policy quarterly

### 2. License Change Monitoring

- **Initialize First:** Always run `--init` before `--check`
- **Run Daily:** Schedule daily checks in CI/CD
- **Review Critically:** Manually verify all CRITICAL changes
- **Pin Versions:** Use exact versions in dependencies to prevent surprise changes

### 3. Alternative Packages

- **Test Thoroughly:** Test alternatives in staging before production
- **Document Replacements:** Track which packages were replaced and why
- **Monitor Quality:** Alternative may have different bugs/features
- **Update Dependencies:** Update imports and code as needed

### 4. Approval Workflows

- **Clear Process:** Define who approves conditional licenses
- **Time Limits:** Set approval timeouts (default: 5 days)
- **Track Approvals:** Keep audit log of all approvals
- **Re-approve Major Versions:** New major versions need re-review

---

## 🔧 Troubleshooting

### Issue: "Policy file not found"

**Solution:**
```bash
# Verify path
ls -la config/company-policy.yml

# Use absolute path
python scripts/policy_checker.py \
  --policy "$(pwd)/config/company-policy.yml" \
  --ort-results ort-results/analyzer/analyzer-result.yml
```

### Issue: "No alternatives found"

**Reasons:**
- Package type not supported yet (only PyPI/NPM implemented)
- Search terms too specific
- No packages with approved licenses exist

**Solution:**
- Manual search on package registry
- Consider relaxing policy temporarily with approval
- Request exception from legal team

### Issue: "License history corrupted"

**Solution:**
```bash
# Backup existing history
cp .ort/license-history.json .ort/license-history.json.backup

# Re-initialize
python scripts/license_change_monitor.py --init \
  --ort-results ort-results/analyzer/analyzer-result.yml

# Restore if needed
mv .ort/license-history.json.backup .ort/license-history.json
```

---

## 📚 Additional Documentation

- **[QUICK_START.md](docs/QUICK_START.md)** - Step-by-step tutorial
- **[POLICY_GUIDE.md](docs/POLICY_GUIDE.md)** - How to configure company policy
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - Script parameters reference
- **[EXAMPLES.md](examples/README.md)** - Real-world examples

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Update documentation
5. Submit pull request

---

## 📄 License

This workflow system is provided as-is under Apache-2.0 license.

---

## 💬 Support

- **Issues:** [GitHub Issues](https://github.com/your-org/repo/issues)
- **Email:** compliance@yourcompany.com
- **Internal Wiki:** [Company Confluence/Wiki Link]

---

## 🎯 Success Metrics

Track effectiveness with these KPIs:

- **Compliance Score:** Target >95%
- **Critical Changes Detected:** 0 missed
- **Forbidden Package Usage:** 0 in production
- **Mean Time to Resolution:** <2 days for policy violations
- **Approval Turnaround:** <24 hours for conditional licenses

---

**Made with ❤️ for software compliance teams**

*Last Updated: 2025-01-16*
