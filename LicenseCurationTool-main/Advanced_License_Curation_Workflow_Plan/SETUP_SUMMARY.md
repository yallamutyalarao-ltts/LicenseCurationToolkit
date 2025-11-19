# 🎉 Advanced License Curation Workflow - Setup Complete!

> **Complete working solution** for managing missing, conflicted, and company-non-compliant licenses

---

## ✅ What Was Created

Your complete Advanced License Curation Workflow is ready to use! Here's what you have:

### 📁 Folder Structure

```
Advanced_License_Curation_Workflow/
├── README.md                    # Main documentation (START HERE!)
├── SETUP_SUMMARY.md            # This file
├── requirements.txt            # Python dependencies
│
├── config/
│   └── company-policy.yml      # ⭐ Company license policy database
│                                   (CONFIGURE THIS FIRST!)
│
├── scripts/
│   ├── policy_checker.py       # ✅ Check packages against policy
│   ├── alternative_package_finder.py  # 🔄 Find replacement packages
│   ├── license_change_monitor.py      # 🔍 Track license changes
│   ├── smart_curation_engine.py       # 🤖 Intelligent decisions (future)
│   └── compliance_dashboard.py        # 📊 Unified reporting (future)
│
├── templates/
│   └── github-workflows/
│       └── license-compliance.yml     # GitHub Actions workflow
│
├── docs/
│   ├── QUICK_START.md          # 15-minute getting started guide
│   └── ...                     # Additional documentation
│
├── examples/
│   └── README.md               # Real-world usage scenarios
│
└── .ort/                       # (Created on first run)
    └── license-history.json    # License change tracking database
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
cd Advanced_License_Curation_Workflow
pip install -r requirements.txt
```

**Required:**
- `pyyaml` - For reading configuration files
- `requests` - For API calls (PyPI, NPM, GitHub)

---

### Step 2: Configure Company Policy

**Edit:** `config/company-policy.yml`

**Minimum Configuration:**

```yaml
company_license_policy:
  company_name: "Your Company Name"  # ← Change this

  # Licenses you allow
  approved_licenses:
    permissive:
      licenses:
        - "MIT"
        - "Apache-2.0"
        - "BSD-3-Clause"

  # Licenses you forbid
  forbidden_licenses:
    proprietary_restricted:
      licenses:
        - "GPL-3.0-only"    # ← Add your forbidden licenses
        - "SSPL-1.0"
        - "Proprietary"
```

**See:** Full configuration examples in the file itself

---

### Step 3: Run First Check

**Assuming you have ORT results:**

```bash
# From your project root (parent of Advanced_License_Curation_Workflow)

python Advanced_License_Curation_Workflow/scripts/policy_checker.py \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --output policy-compliance-report.html

# Open report
start policy-compliance-report.html  # Windows
# or
open policy-compliance-report.html   # Mac/Linux
```

**Don't have ORT results yet?**

```bash
# Install ORT first
ORT_VERSION="70.0.1"
wget https://github.com/oss-review-toolkit/ort/releases/download/${ORT_VERSION}/ort-${ORT_VERSION}.tgz
tar -xzf ort-${ORT_VERSION}.tgz
export PATH="${PWD}/ort-${ORT_VERSION}/bin:$PATH"

# Run ORT analysis
ort analyze -i . -o ort-results/analyzer

# Then run policy check
python Advanced_License_Curation_Workflow/scripts/policy_checker.py \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --output policy-compliance-report.html
```

---

## 🎯 Core Features Implemented

### 1️⃣ Policy-Based Compliance Check ✅

**Script:** `scripts/policy_checker.py`

**What it does:**
- Checks all packages against company policy
- Categorizes licenses as:
  - ✅ Approved (green)
  - ⚠️ Conditional (yellow - needs approval)
  - ❌ Forbidden (red - cannot use)
  - ❓ Unknown (gray - needs research)
- Generates compliance score (0-100%)
- Exports HTML report + JSON for automation

**Example:**
```bash
python scripts/policy_checker.py \
  --policy config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --output policy-report.html \
  --json policy-results.json
```

**Output:**
```
✅ Analyzed 50 packages
   ✅ Approved:    42 (84%)
   ⚠️  Conditional: 5  (10%)
   ❌ Forbidden:   2  (4%)
   ❓ Unknown:     1  (2%)
   📈 Compliance Score: 84%
```

---

### 2️⃣ Alternative Package Finder ✅

**Script:** `scripts/alternative_package_finder.py`

**What it does:**
- Finds replacement packages when forbidden license detected
- Searches PyPI/NPM registries
- Ranks alternatives by:
  - License compatibility (40%)
  - Popularity (25%)
  - Maintenance (20%)
  - Documentation (10%)
  - Security (5%)
- Generates comparison report

**Example:**
```bash
python scripts/alternative_package_finder.py \
  --package "pycutest" \
  --type "PyPI" \
  --forbidden-license "GPL-3.0-or-later" \
  --policy config/company-policy.yml \
  --output alternatives-pycutest.html
```

**Output:**
```
✅ Found 5 alternatives

Top 3 recommendations:
  1. cutest-alternative (MIT) - Score: 0.92
  2. optimization-lib (Apache-2.0) - Score: 0.88
  3. solver-toolkit (BSD-3-Clause) - Score: 0.85
```

---

### 3️⃣ License Change Monitor ✅

**Script:** `scripts/license_change_monitor.py`

**What it does:**
- Tracks license history over time
- Detects when packages change licenses
- Assesses severity:
  - ⛔ CRITICAL: Permissive → Copyleft (MIT → GPL)
  - ⚠️ HIGH: Unusual changes
  - 📋 MEDIUM: License family changes
  - ℹ️ LOW: Minor version changes
- Generates alert report with recommended actions

**First-time setup:**
```bash
python scripts/license_change_monitor.py --init \
  --ort-results ort-results/analyzer/analyzer-result.yml
```

**Daily monitoring:**
```bash
python scripts/license_change_monitor.py --check \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --policy config/company-policy.yml \
  --output license-changes-report.html \
  --fail-on-critical
```

**Output:**
```
📊 Results:
   Total changes detected: 3
   ⛔ Critical: 1 (requests: MIT → GPL-3.0)
   ⚠️  High:     1
   📋 Medium:   1

❌ CRITICAL LICENSE CHANGES DETECTED!
```

---

## 📊 Reports Generated

### 1. Policy Compliance Report

**File:** `policy-compliance-report.html`

**Contents:**
- Beautiful HTML report with:
  - Compliance score gauge (0-100%)
  - Package-by-package status
  - Risk level indicators
  - Required actions and approvals
  - Conditions for conditional licenses

**Visual:**
- 🟢 Green rows: Approved packages
- 🟡 Yellow rows: Need approval
- 🔴 Red rows: Forbidden (URGENT)
- ⚪ Gray rows: Unknown (research needed)

---

### 2. License Change Alert

**File:** `license-changes-report.html`

**Contents:**
- Detected license changes since last scan
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
- Direct links to verify (PyPI, homepage, repository)
- Overall score for each alternative

---

## 🔄 Complete Workflow Example

**Daily compliance check script:**

```bash
#!/bin/bash
# daily-compliance-check.sh

set -e

echo "🔍 Daily License Compliance Check"
echo "=================================="

# Step 1: Run ORT analysis
echo "1. Running ORT analysis..."
ort analyze -i . -o ort-results/analyzer

# Step 2: Check policy compliance
echo "2. Checking policy compliance..."
python Advanced_License_Curation_Workflow/scripts/policy_checker.py \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --output reports/policy-compliance-$(date +%Y-%m-%d).html \
  --json reports/policy-results.json

# Step 3: Check for license changes
echo "3. Checking for license changes..."
python Advanced_License_Curation_Workflow/scripts/license_change_monitor.py --check \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
  --output reports/license-changes-$(date +%Y-%m-%d).html

# Step 4: Find alternatives for forbidden packages
echo "4. Checking for forbidden packages..."
FORBIDDEN_COUNT=$(python -c "
import json
with open('reports/policy-results.json') as f:
    data = json.load(f)
print(data['summary']['forbidden'])
")

if [ "$FORBIDDEN_COUNT" -gt 0 ]; then
    echo "⚠️  $FORBIDDEN_COUNT forbidden packages found!"
    echo "   Review policy report and run alternative finder manually"
fi

echo ""
echo "✅ Compliance check complete!"
echo "📊 Reports:"
echo "   - reports/policy-compliance-$(date +%Y-%m-%d).html"
echo "   - reports/license-changes-$(date +%Y-%m-%d).html"
```

**Make executable and run:**
```bash
chmod +x daily-compliance-check.sh
./daily-compliance-check.sh
```

---

## 🤖 GitHub Actions Integration

**Copy template to your repository:**

```bash
mkdir -p .github/workflows
cp Advanced_License_Curation_Workflow/templates/github-workflows/license-compliance.yml \
   .github/workflows/
```

**Commit and push:**

```bash
git add .github/workflows/license-compliance.yml
git add Advanced_License_Curation_Workflow/
git commit -m "Add advanced license compliance workflow"
git push
```

**What it does:**
- Runs on every push/PR + daily at 2 AM
- Checks policy compliance
- Detects license changes
- Comments on PRs with compliance status
- Fails build if critical issues found
- Deploys reports to GitHub Pages (optional)

---

## 📚 Documentation

### Essential Reading

1. **[README.md](README.md)** - Complete documentation
   - Features overview
   - Configuration guide
   - All script parameters
   - Best practices
   - Troubleshooting

2. **[docs/QUICK_START.md](docs/QUICK_START.md)** - 15-minute tutorial
   - Step-by-step walkthrough
   - Real example
   - Common issues

3. **[examples/README.md](examples/README.md)** - Real-world scenarios
   - New project setup
   - Dealing with forbidden licenses
   - License change response
   - Conditional approval workflow
   - Unknown license research

### Configuration Reference

- **[config/company-policy.yml](config/company-policy.yml)** - Policy database
  - Approved licenses
  - Conditional licenses (need approval)
  - Forbidden licenses
  - License compatibility matrix
  - Alternative package preferences
  - Notification settings

---

## 🎯 Your Use Cases Solved

### ✅ Use Case 1: Missing Licenses

**Problem:** Package has `NOASSERTION` or `UNKNOWN` license

**Solution:**
```bash
# 1. Policy checker identifies unknown packages
python scripts/policy_checker.py --policy config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml

# 2. Manually research (see examples/README.md Scenario 5)
# 3. Add curation with findings documented
```

---

### ✅ Use Case 2: Conflicted Licenses

**Problem:** ORT says "MIT", ScanCode says "GPL-3.0", PyPI says "Apache-2.0"

**Solution:**
- Use policy checker to flag conflict
- Manually verify from source repository
- Use smart curation engine (future feature) for AI-assisted resolution
- Document decision in curation with evidence

---

### ✅ Use Case 3: Company Non-Compliant

**Problem:** Package has GPL-3.0, company forbids copyleft licenses

**Solution:**
```bash
# 1. Policy checker identifies as FORBIDDEN
python scripts/policy_checker.py --policy config/company-policy.yml

# 2. Find alternatives
python scripts/alternative_package_finder.py \
  --package "forbidden-package" \
  --type "PyPI" \
  --forbidden-license "GPL-3.0-only" \
  --policy config/company-policy.yml

# 3. Choose best alternative from report
# 4. Replace package in dependencies
# 5. Test thoroughly
# 6. Re-run compliance check
```

---

### ✅ Use Case 4: Suddenly Changed License

**Problem:** Package version 1.0 was MIT, version 2.0 is now GPL-3.0

**Solution:**
```bash
# 1. License change monitor detects and alerts
python scripts/license_change_monitor.py --check

# 2. Follow recommended actions in alert report:
#    - Pin to previous version
#    - Find alternative
#    - Contact package maintainer

# 3. Document incident
# 4. Update CI/CD to prevent future surprises
```

---

## 🔧 Next Steps

### Immediate (Today)

1. **Configure company policy** (`config/company-policy.yml`)
   - Add your forbidden licenses
   - Define approved licenses
   - Set up approvers for conditional licenses

2. **Run first compliance check**
   - Generate policy report
   - Review results
   - Address any critical issues

3. **Initialize license tracking**
   - Set up baseline history
   - Enable change detection

### This Week

1. **Integrate into CI/CD**
   - Copy GitHub Actions workflow
   - Test in staging environment
   - Enable for production

2. **Document processes**
   - Approval workflow for conditional licenses
   - Incident response for license changes
   - Package replacement procedures

3. **Train team**
   - Share documentation
   - Walk through example scenarios
   - Set up notification channels

### This Month

1. **Build audit trail**
   - Track all approvals
   - Document all curations
   - Regular compliance reports

2. **Optimize workflow**
   - Adjust policy based on needs
   - Fine-tune ranking weights for alternatives
   - Reduce false positives

3. **Establish metrics**
   - Target: >95% compliance score
   - Track forbidden package detections
   - Measure time-to-resolution

---

## 🆘 Getting Help

### Common Questions

**Q: Do I need to configure everything in company-policy.yml?**
A: No! Start with just `approved_licenses` and `forbidden_licenses`. The rest has sensible defaults.

**Q: Can I use this without ORT?**
A: The policy checker requires ORT results format. However, you can adapt scripts to work with other SBOM formats.

**Q: What if alternative finder doesn't find anything?**
A: Manual search required. Use package registry search, ask community, or request exception from legal team.

**Q: How often should I run license checks?**
A: Daily in CI/CD (automated), plus before every release (manual review).

### Support Channels

- **Documentation:** [README.md](README.md)
- **Examples:** [examples/README.md](examples/README.md)
- **Issues:** GitHub Issues (if applicable)
- **Email:** compliance@yourcompany.com

---

## 🎉 You're All Set!

Your Advanced License Curation Workflow is ready to use!

**Start with:**
```bash
# 1. Configure policy
nano config/company-policy.yml

# 2. Run first check
python scripts/policy_checker.py \
  --policy config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --output policy-report.html

# 3. Open report
open policy-report.html
```

---

**Made with ❤️ for compliance teams**

*Setup completed: 2025-01-16*
