# Advanced License Curation Workflow Components

> Comprehensive solution for ORT license analysis with policy enforcement, change monitoring, alternative package recommendations, Smart Curation Engine, and Compliance Dashboard

[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
[![ORT](https://img.shields.io/badge/ORT-70.0.1-green.svg)](https://github.com/oss-review-toolkit/ort)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Workflow Architecture](#workflow-architecture)
- [Components](#components)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Reports Generated](#reports-generated)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This integrated workflow combines the power of ORT, ScanCode, PyPI API, and AI-powered analysis with advanced policy enforcement, license change tracking, and automated alternative package recommendations.

### What Problems Does This Solve?

**1. Missing Licenses**
- Packages with `NOASSERTION`, `UNKNOWN`, or blank licenses
- Multi-source detection: PyPI API → ScanCode → AI suggestions

**2. Conflicted Licenses**
- Different tools report different licenses (ORT vs ScanCode vs PyPI)
- AI-powered conflict resolution with evidence-based recommendations

**3. Company Non-Compliant Licenses**
- Automatic detection of forbidden licenses (GPL, SSPL, etc.)
- Instant alternative package recommendations with ranking

**4. Suddenly Changed Licenses**
- Historical tracking with severity assessment (CRITICAL/HIGH/MEDIUM/LOW)
- Automated alerts for permissive → copyleft changes
- Action plans for remediation

**5. Policy Enforcement**
- Centralized company policy configuration
- Automated compliance scoring (0-100%)
- Approval workflows for conditional licenses

---

## ✨ Features

### 🔒 Policy-Based License Management
- Define approved/conditional/forbidden licenses
- Automatic policy enforcement during CI/CD
- License compatibility matrix
- Approval workflows with configurable approvers

### 🔄 License Change Detection
- Historical tracking database (`.ort/license-history.json`)
- Automatic severity assessment
- Alert generation for critical changes
- Permissive-to-Copyleft detection

### 🔍 Alternative Package Finder
- Automatic search for compliant alternatives
- Multi-factor ranking:
  - License compatibility (40%)
  - Popularity/downloads (25%)
  - Maintenance status (20%)
  - Documentation quality (10%)
  - Security track record (5%)
- Side-by-side comparison reports

### 🤖 Multi-Source License Detection
1. **ORT Analyzer** - Package manager metadata
2. **Policy Checker** - Company policy enforcement
3. **License Change Monitor** - Historical tracking
4. **PyPI API** - Fast registry lookup
5. **ScanCode** - Deep source code scanning
6. **AI Analysis** - Intelligent conflict resolution

### 📊 Comprehensive Reporting
- Policy compliance report (HTML + JSON)
- License change alerts with severity
- Alternative packages report
- Multiple AI-powered curation reports
- Enhanced SPDX documents
- Unified GitHub Pages dashboard

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.11+ with pip
python --version

# ORT installed (or use workflow auto-install)
ort --version

# Install Python dependencies
pip install -r workflow_components/requirements.txt
```

### 5-Minute Setup

```bash
# 1. Configure company policy
nano workflow_components/config/company-policy.yml

# Edit approved/forbidden licenses for your organization

# 2. Copy workflow to your repository
cp workflow_components/advanced-integrated-workflow.yml .github/workflows/

# 3. Set up GitHub secrets (for AI features)
# - AZURE_OPENAI_API_KEY
# - AZURE_OPENAI_ENDPOINT
# - AZURE_OPENAI_MODEL (optional)

# 4. Commit and push
git add .github/workflows/advanced-integrated-workflow.yml
git add workflow_components/
git commit -m "Add advanced license curation workflow"
git push
```

**That's it!** The workflow runs automatically on every push/PR and daily at 2 AM for license change monitoring.

---

## 🏗️ Workflow Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                Source Code / Dependencies                      │
└────────────────┬───────────────────────────────────────────────┘
                 │
     ┌───────────▼───────────┐
     │  STAGE 1: ORT         │
     │  - Analyzer           │
     │  - Advisor (OSV)      │
     │  - Reporter           │
     └───────────┬───────────┘
                 │
     ┌───────────▼─────────────────┐
     │  STAGE 2: Policy Check      │ ◄─── company-policy.yml
     │  - Approved/Forbidden       │
     │  - Conditional licenses     │
     │  - Compliance scoring       │
     └───────────┬─────────────────┘
                 │
     ┌───────────▼─────────────────┐
     │  STAGE 3: Change Monitor    │ ◄─── .ort/license-history.json
     │  - Historical tracking      │
     │  - Severity assessment      │
     │  - Alert generation         │
     └───────────┬─────────────────┘
                 │
     ┌───────────▼─────────────────┐
     │  STAGE 4: Find Alternatives │ ◄─── Forbidden packages
     │  - PyPI/NPM search          │
     │  - Multi-factor ranking     │
     │  - Comparison reports       │
     └───────────┬─────────────────┘
                 │
     ┌───────────▼─────────────────┐
     │  STAGE 5-7: Multi-Source    │
     │  - Extract uncertain pkgs   │
     │  - PyPI API fetch           │
     │  - ScanCode deep scan       │
     │  - SPDX enhancement         │
     └───────────┬─────────────────┘
                 │
     ┌───────────▼─────────────────┐
     │  STAGE 8-9: AI Analysis     │ ◄─── Azure OpenAI
     │  - Main curation report     │
     │  - Conflict resolution      │
     │  - Missing license research │
     │  - Multi-layer comparison   │
     └───────────┬─────────────────┘
                 │
     ┌───────────▼─────────────────┐
     │  STAGE 10-11: Deploy        │
     │  - GitHub Pages             │
     │  - Artifact upload          │
     │  - PR comments              │
     └─────────────────────────────┘
```

---

## 📦 Components

### Scripts (`scripts/`)

#### 1. `policy_checker.py`
**Purpose:** Check all packages against company policy

**Features:**
- Categorizes licenses as approved/conditional/forbidden/unknown
- Calculates compliance score (0-100%)
- Generates HTML report + JSON export
- Fails build if forbidden packages detected

**Usage:**
```bash
python3 scripts/policy_checker.py \
  --policy config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --output policy-compliance-report.html \
  --json policy-results.json
```

#### 2. `license_change_monitor.py`
**Purpose:** Track license changes over time

**Features:**
- Historical database (`.ort/license-history.json`)
- Severity assessment (CRITICAL/HIGH/MEDIUM/LOW)
- Detects permissive → copyleft changes
- Generates alerts with recommended actions

**Usage:**
```bash
# First run - initialize tracking
python3 scripts/license_change_monitor.py --init \
  --ort-results ort-results/analyzer/analyzer-result.yml

# Subsequent runs - check for changes
python3 scripts/license_change_monitor.py --check \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --policy config/company-policy.yml \
  --output license-changes-report.html \
  --fail-on-critical
```

#### 3. `alternative_package_finder.py`
**Purpose:** Find replacement packages for forbidden licenses

**Features:**
- Searches PyPI/NPM registries
- Multi-factor ranking (license, popularity, maintenance, docs, security)
- Side-by-side comparison
- Direct links to verify alternatives

**Usage:**
```bash
python3 scripts/alternative_package_finder.py \
  --package "pycutest" \
  --type "PyPI" \
  --forbidden-license "GPL-3.0-or-later" \
  --policy config/company-policy.yml \
  --output alternatives-pycutest.html \
  --max-results 5
```

#### 4. `smart_curation_engine.py` ⭐ NEW
**Purpose:** Combine multi-source evidence to generate intelligent curation suggestions

**Features:**
- Consolidates data from policy checker, ORT, PyPI, ScanCode
- Confidence scoring for each curation suggestion
- Evidence-based recommendations
- Automatic high-confidence curations
- Manual review queue for uncertain cases

**Usage:**
```bash
python3 scripts/smart_curation_engine.py \
  --policy config/company-policy.yml \
  --policy-json policy-reports/policy-results.json \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --pypi-json pypi-licenses/pypi-licenses-full.json \
  --scancode-dir scancode-results \
  --output-curations smart-curations.yml \
  --output-review manual-review-queue.html \
  --output-stats curation-stats.json
```

**Outputs:**
- `smart-curations.yml` - High-confidence curation suggestions (≥70%)
- `manual-review-queue.html` - Beautiful HTML report for packages requiring manual verification
- `curation-stats.json` - Statistics summary (total packages, confidence distribution)

**Key Features:**
- **Multi-Source Evidence:** Combines ORT declared/concluded, PyPI API, ScanCode detections
- **Confidence Scoring:** 0-100% confidence based on source agreement and policy compliance
- **Smart Filtering:** Only suggests curations for uncertain packages (skips already approved)
- **Manual Review Workflow:** Flags low-confidence suggestions (<70%) for human verification

#### 5. `compliance_dashboard.py` ⭐ NEW
**Purpose:** Generate unified executive dashboard for all compliance metrics

**Features:**
- Overall compliance score and risk assessment
- Policy compliance breakdown (approved/conditional/forbidden/unknown)
- License change alerts summary
- Smart curation statistics
- Priority action items (sorted by severity)
- Links to all detailed reports

**Usage:**
```bash
python3 scripts/compliance_dashboard.py \
  --policy-json policy-reports/policy-results.json \
  --changes-json license-changes.json \
  --curation-stats curation-stats.json \
  --reports-dir public \
  --output compliance-dashboard.html
```

**Outputs:**
- `compliance-dashboard.html` - Executive-level compliance overview

**Dashboard Includes:**
- 📊 **Overall Compliance Score** - Weighted average with risk level (LOW/MEDIUM/HIGH/CRITICAL)
- ✅ **Policy Compliance** - Visual breakdown with percentage bars
- 🔄 **License Changes** - Summary by severity (Critical/High/Medium/Low)
- 🤖 **Smart Curation Results** - Total suggestions and manual review count
- ⚡ **Priority Action Items** - Top 10 actions sorted by urgency
- 📄 **Available Reports** - Auto-detected links to all generated reports

**Risk Calculation:**
- Base score from policy compliance
- Penalties for critical changes (-10% each, max -20%)
- Penalties for forbidden packages (-15% each, max -30%)
- Risk levels: >90% = LOW, 75-90% = MEDIUM, 60-75% = HIGH, <60% = CRITICAL

### Configuration (`config/`)

#### `company-policy.yml`
**Purpose:** Centralized license policy database

**Key Sections:**

1. **Approved Licenses**
   ```yaml
   approved_licenses:
     permissive:
       licenses:
         - "MIT"
         - "Apache-2.0"
         - "BSD-3-Clause"
       auto_approve: true
       risk_level: "low"
   ```

2. **Conditional Licenses** (require approval)
   ```yaml
   conditional_licenses:
     strong_copyleft:
       licenses:
         - "GPL-3.0-only"
         - "AGPL-3.0-only"
       approval_required: true
       approvers:
         - "legal@company.com"
       risk_level: "high"
   ```

3. **Forbidden Licenses**
   ```yaml
   forbidden_licenses:
     proprietary_restricted:
       licenses:
         - "SSPL-1.0"
         - "Elastic-2.0"
       reason: "Incompatible with company business model"
       action: "reject"
   ```

4. **License Compatibility Matrix**
   ```yaml
   license_compatibility:
     - combination: "MIT AND Apache-2.0"
       compatible: true
     - combination: "Apache-2.0 AND GPL-2.0-only"
       compatible: false
       reason: "Apache patent clause incompatible with GPL-2.0"
   ```

---

## 📥 Installation

### Option 1: GitHub Actions (Recommended)

```bash
# 1. Copy workflow to your repository
mkdir -p .github/workflows
cp workflow_components/advanced-integrated-workflow.yml .github/workflows/

# 2. Copy workflow components
cp -r workflow_components/ .

# 3. Configure policy
nano workflow_components/config/company-policy.yml

# 4. Set up GitHub secrets
# Go to Settings → Secrets → Actions → New repository secret
# Add:
#   - AZURE_OPENAI_API_KEY
#   - AZURE_OPENAI_ENDPOINT
#   - AZURE_OPENAI_MODEL (optional, defaults to gpt-4.1-mini)

# 5. Commit and push
git add .github/workflows/ workflow_components/
git commit -m "Add advanced license curation workflow"
git push
```

### Option 2: Local Development

```bash
# 1. Install dependencies
pip install -r workflow_components/requirements.txt

# 2. Install ORT
ORT_VERSION="70.0.1"
wget https://github.com/oss-review-toolkit/ort/releases/download/${ORT_VERSION}/ort-${ORT_VERSION}.tgz
tar -xzf ort-${ORT_VERSION}.tgz
export PATH="${PWD}/ort-${ORT_VERSION}/bin:$PATH"

# 3. Configure policy
nano workflow_components/config/company-policy.yml

# 4. Run analysis
# See "Usage" section below
```

---

## ⚙️ Configuration

### 1. Company Policy

**File:** `workflow_components/config/company-policy.yml`

**Minimum Configuration:**
```yaml
company_license_policy:
  company_name: "Your Company Name"  # ← Change this

  approved_licenses:
    permissive:
      licenses:
        - "MIT"
        - "Apache-2.0"
        - "BSD-3-Clause"

  forbidden_licenses:
    proprietary_restricted:
      licenses:
        - "SSPL-1.0"        # ← Add your forbidden licenses
        - "GPL-3.0-only"
        - "Proprietary"
```

**Best Practices:**
- Start conservative (strict policy), loosen as needed
- Document why licenses are forbidden
- Version control the policy file
- Review quarterly

### 2. Azure OpenAI (Optional, for AI features)

**Required Secrets:**
- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI service endpoint
- `AZURE_OPENAI_MODEL` - Your deployment name (e.g., `gpt-4o-mini`)

**Cost Estimate:**
- ~$0.20-$0.33 per workflow run (with all AI features)
- ~$6-$10 per month per repository (daily runs)

### 3. License History Tracking

**File:** `.ort/license-history.json` (auto-created)

**Initialization:**
```bash
python3 workflow_components/scripts/license_change_monitor.py --init \
  --ort-results ort-results/analyzer/analyzer-result.yml
```

**Commit to Git?** Yes! - Version control provides audit trail

---

## 🎮 Usage

### Complete Workflow (Recommended)

The GitHub Actions workflow runs automatically:
- On every push to `main`/`master`/`develop`
- On every pull request
- Daily at 2 AM UTC (for license change monitoring)
- Manual trigger via `workflow_dispatch`

### Manual Execution

#### 1. Policy Compliance Check

```bash
# Run ORT analysis first
ort analyze -i . -o ort-results/analyzer

# Check policy compliance
python3 workflow_components/scripts/policy_checker.py \
  --policy workflow_components/config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --output policy-compliance-report.html \
  --json policy-results.json

# View report
open policy-compliance-report.html
```

**Example Output:**
```
✅ Analyzed 50 packages
   ✅ Approved:    42 (84%)
   ⚠️  Conditional: 5  (10%)
   ❌ Forbidden:   2  (4%)
   ❓ Unknown:     1  (2%)
   📈 Compliance Score: 84%

❌ FORBIDDEN PACKAGES DETECTED:
   - pycutest/2.1.0 (GPL-3.0-or-later)
   - mongodb/4.0.0 (SSPL-1.0)
```

#### 2. License Change Monitoring

```bash
# First run - initialize
python3 workflow_components/scripts/license_change_monitor.py --init \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --history .ort/license-history.json

# Subsequent runs - check for changes
python3 workflow_components/scripts/license_change_monitor.py --check \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --policy workflow_components/config/company-policy.yml \
  --output license-changes-report.html \
  --json license-changes.json \
  --fail-on-critical

# View report
open license-changes-report.html
```

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

Recommended Actions:
   1. Pin to previous version: requests==2.27.1
   2. Find alternative package
   3. Contact package maintainer
```

#### 3. Find Alternative Packages

```bash
# Find alternatives for a forbidden package
python3 workflow_components/scripts/alternative_package_finder.py \
  --package "pycutest" \
  --type "PyPI" \
  --forbidden-license "GPL-3.0-or-later" \
  --policy workflow_components/config/company-policy.yml \
  --output alternatives-pycutest.html \
  --max-results 5

# View report
open alternatives-pycutest.html
```

**Example Output:**
```
✅ Found 5 alternatives

Top 3 recommendations:
  1. cutest-alternative (MIT) - Score: 0.92
     ↳ Downloads: 50K/month | Stars: 500 | Last update: 2 days ago
     ↳ Homepage: https://...
     ↳ Repository: https://github.com/...

  2. optimization-lib (Apache-2.0) - Score: 0.88
     ↳ Downloads: 30K/month | Stars: 300 | Last update: 1 week ago

  3. solver-toolkit (BSD-3-Clause) - Score: 0.85
     ↳ Downloads: 20K/month | Stars: 200 | Last update: 2 weeks ago
```

---

## 📊 Reports Generated

### 1. Policy Compliance Report
**File:** `policy-compliance-report.html`

**Contents:**
- Compliance score gauge (0-100%)
- Package-by-package status
- Risk level indicators
- Required approvals
- Conditions for conditional licenses

**Visual Indicators:**
- 🟢 Green: Approved packages
- 🟡 Yellow: Need approval
- 🔴 Red: Forbidden (URGENT)
- ⚪ Gray: Unknown (research needed)

---

### 2. License Change Alert
**File:** `license-changes-report.html`

**Contents:**
- Detected changes since last scan
- Severity badges (CRITICAL/HIGH/MEDIUM/LOW)
- Before/After license comparison
- Risk assessment for each change
- Step-by-step recommended actions

---

### 3. Alternative Packages Report
**File:** `alternatives-{package}.html`

**Contents:**
- Top 5 alternative packages
- License comparison
- Popularity metrics (downloads, GitHub stars)
- Maintenance status (last update)
- Direct links to verify
- Overall compatibility score

---

### 4. AI Curation Reports
**Files:** `curation-report-*.html`

**Types:**
- Main ORT curation report (comprehensive analysis)
- Conflict resolution report (ORT vs ScanCode conflicts)
- Missing licenses analysis (AI research suggestions)
- Multi-layer comparison (all sources combined)

---

### 5. GitHub Pages Dashboard

**URL:** `https://<your-org>.github.io/<your-repo>/`

**Includes:**
- All reports listed above
- ORT WebApp (interactive dependency explorer)
- ORT StaticHTML report
- ScanCode native reports
- PyPI license fetch results
- Enhanced SPDX documents
- CycloneDX SBOM

---

## 📝 Best Practices

### 1. Policy Management
✅ **DO:**
- Start with strict policy, loosen as needed
- Document reasons for forbidden licenses
- Version control `company-policy.yml`
- Review and update quarterly
- Involve legal/compliance teams

❌ **DON'T:**
- Approve licenses without understanding implications
- Skip documentation
- Ignore conditional license requirements

### 2. License Change Monitoring
✅ **DO:**
- Run `--init` before first `--check`
- Schedule daily checks in CI/CD
- Manually verify CRITICAL changes
- Pin dependency versions to prevent surprises
- Commit `.ort/license-history.json` to git

❌ **DON'T:**
- Skip initialization
- Ignore CRITICAL alerts
- Auto-update dependencies without review

### 3. Alternative Packages
✅ **DO:**
- Test alternatives thoroughly in staging
- Document replacements and reasons
- Monitor quality/features of alternatives
- Update imports and code as needed
- Get approval for production use

❌ **DON'T:**
- Replace without testing
- Assume same behavior
- Skip documentation

### 4. Approval Workflows
✅ **DO:**
- Define clear approval process
- Set approval timeouts (default: 5 days)
- Keep audit log of approvals
- Re-approve for major version changes
- Involve legal team for high-risk licenses

❌ **DON'T:**
- Auto-approve conditional licenses
- Skip legal review
- Ignore approval requirements

---

## 🔧 Troubleshooting

### Issue: Policy file not found

**Solution:**
```bash
# Verify path
ls -la workflow_components/config/company-policy.yml

# Use absolute path in command
python3 scripts/policy_checker.py \
  --policy "$(pwd)/workflow_components/config/company-policy.yml" \
  --ort-results ort-results/analyzer/analyzer-result.yml
```

---

### Issue: No alternatives found

**Reasons:**
- Package type not supported yet (only PyPI/NPM implemented)
- Search terms too specific
- No packages with approved licenses exist

**Solutions:**
- Manual search on package registry
- Consider relaxing policy temporarily with approval
- Request exception from legal team
- Check if commercial license available

---

### Issue: License history corrupted

**Solution:**
```bash
# Backup existing history
cp .ort/license-history.json .ort/license-history.json.backup

# Re-initialize
python3 scripts/license_change_monitor.py --init \
  --ort-results ort-results/analyzer/analyzer-result.yml

# Restore if needed
mv .ort/license-history.json.backup .ort/license-history.json
```

---

### Issue: Workflow fails on forbidden packages

**Expected Behavior:** This is intentional!

**Solutions:**
1. Find alternatives using `alternative_package_finder.py`
2. Request exception from legal team
3. Pin to previous version with compliant license
4. Update `company-policy.yml` if policy changed

---

### Issue: Azure OpenAI errors

**Check:**
```bash
# Verify secrets configured
echo $AZURE_OPENAI_API_KEY    # Should show key
echo $AZURE_OPENAI_ENDPOINT   # Should show URL

# Test connection
curl -H "api-key: $AZURE_OPENAI_API_KEY" \
     "$AZURE_OPENAI_ENDPOINT/openai/deployments?api-version=2025-01-01-preview"
```

**Common Issues:**
- Incorrect deployment name in `AZURE_OPENAI_MODEL`
- Endpoint missing `/` at the end
- API key expired or invalid
- Rate limit exceeded

---

## 📚 Additional Documentation

- **[QUICK_SETUP.md](docs/QUICK_SETUP.md)** - 15-minute getting started guide
- **[POLICY_GUIDE.md](docs/POLICY_GUIDE.md)** - How to configure company policy
- **[WORKFLOW_DIAGRAM.md](docs/WORKFLOW_DIAGRAM.md)** - Detailed workflow architecture
- **[../CLAUDE.md](../CLAUDE.md)** - Complete system documentation

---

## 🎯 Success Metrics

Track effectiveness with these KPIs:

- **Compliance Score:** Target >95%
- **Critical Changes Detected:** 0 missed
- **Forbidden Package Usage:** 0 in production
- **Mean Time to Resolution:** <2 days for policy violations
- **Approval Turnaround:** <24 hours for conditional licenses

---

## 💬 Support

- **Issues:** Check [Troubleshooting](#troubleshooting) above
- **Documentation:** [README.md](../README.md) and [CLAUDE.md](../CLAUDE.md)
- **GitHub Issues:** [Report bugs/features](https://github.com/your-org/repo/issues)

---

## 📄 License

This workflow system is provided under Apache-2.0 license.

---

**Made with ❤️ for software compliance teams**

*Last Updated: 2025-01-19*
