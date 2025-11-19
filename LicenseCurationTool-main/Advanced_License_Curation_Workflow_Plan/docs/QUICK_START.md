# Quick Start Guide

> Get up and running with Advanced License Curation in 15 minutes

---

## Step 1: Verify Prerequisites (2 minutes)

**Check Python:**
```bash
python --version
# Should be 3.8 or higher
```

**Check ORT (Optional but recommended):**
```bash
ort --version
# If not installed, see: https://github.com/oss-review-toolkit/ort#installation
```

**Install Required Python Packages:**
```bash
pip install pyyaml requests
```

---

## Step 2: Copy Workflow to Your Project (1 minute)

```bash
# Navigate to your project root
cd /path/to/your/project

# Copy the Advanced_License_Curation_Workflow folder
cp -r /path/to/Advanced_License_Curation_Workflow .

# Verify structure
ls Advanced_License_Curation_Workflow/
# Should see: config/ scripts/ docs/ examples/ templates/
```

---

## Step 3: Configure Company Policy (3 minutes)

Edit `Advanced_License_Curation_Workflow/config/company-policy.yml`:

**Minimal Configuration:**

```yaml
company_license_policy:
  company_name: "My Company"  # ← Change this

  approved_licenses:
    permissive:
      licenses:
        - "MIT"
        - "Apache-2.0"
        - "BSD-3-Clause"
      auto_approve: true

  forbidden_licenses:
    proprietary_restricted:
      licenses:
        - "GPL-3.0-only"      # ← Add your forbidden licenses
        - "SSPL-1.0"
        - "Proprietary"
      action: "reject"
```

**Save the file.**

---

## Step 4: Run Your First Scan (5 minutes)

### Option A: If you have existing ORT results

```bash
# Assuming you already ran ORT:
# ort analyze -i . -o ort-results/analyzer

# Check policy compliance
python Advanced_License_Curation_Workflow/scripts/policy_checker.py \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --output policy-compliance-report.html
```

### Option B: Run complete workflow from scratch

```bash
# 1. Run ORT analysis
ort analyze -i . -o ort-results/analyzer

# 2. Check policy compliance
python Advanced_License_Curation_Workflow/scripts/policy_checker.py \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --output policy-compliance-report.html

# 3. Initialize license change tracking
python Advanced_License_Curation_Workflow/scripts/license_change_monitor.py --init \
  --ort-results ort-results/analyzer/analyzer-result.yml
```

---

## Step 5: Review Results (4 minutes)

**Open the compliance report:**

- **Windows:** `start policy-compliance-report.html`
- **Linux:** `xdg-open policy-compliance-report.html`
- **Mac:** `open policy-compliance-report.html`

**What to look for:**

1. **Compliance Score** - Should be >80% for healthy projects
2. **Forbidden Packages** (Red) - These MUST be addressed
3. **Unknown Packages** (Gray) - Need research
4. **Conditional Packages** (Yellow) - Need approval

---

## Step 6: Handle Forbidden Packages (If Any)

**If you see forbidden packages:**

```bash
# Example: Package "pycutest" has forbidden license "GPL-3.0"

python Advanced_License_Curation_Workflow/scripts/alternative_package_finder.py \
  --package "pycutest" \
  --type "PyPI" \
  --forbidden-license "GPL-3.0-or-later" \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
  --output alternatives-pycutest.html
```

**Review alternatives:**

```bash
# Open alternatives report
open alternatives-pycutest.html

# Top alternatives will be ranked by:
# - License compatibility
# - Popularity
# - Maintenance status
```

---

## Real Example Walkthrough

Let's say you have the following packages in your project:

```
packages:
  ✅ requests (Apache-2.0) - APPROVED
  ⚠️  numpy (BSD License) - UNKNOWN (needs normalization)
  ❌ pycutest (GPL-3.0-or-later) - FORBIDDEN
  ❓ setuptools (NOASSERTION) - UNKNOWN
```

### Step-by-Step Resolution:

#### 1. **requests (Apache-2.0)** - ✅ APPROVED
- No action needed
- Automatically approved by policy

#### 2. **numpy (BSD License)** - ⚠️ UNKNOWN
- Need to normalize license
- "BSD License" → likely "BSD-3-Clause"
- **Action:** Add to policy or manually curate

```bash
# Option 1: Add to policy (if you trust all BSD licenses)
nano Advanced_License_Curation_Workflow/config/company-policy.yml
# Add "BSD License" to approved_licenses

# Option 2: Manually curate
# (Use main curation workflow from parent directory)
```

#### 3. **pycutest (GPL-3.0-or-later)** - ❌ FORBIDDEN
- **Action:** Find alternative

```bash
python Advanced_License_Curation_Workflow/scripts/alternative_package_finder.py \
  --package "pycutest" \
  --type "PyPI" \
  --forbidden-license "GPL-3.0-or-later" \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
  --output alternatives-pycutest.html

# Review suggestions and replace package
```

#### 4. **setuptools (NOASSERTION)** - ❓ UNKNOWN
- Setuptools is actually MIT licensed
- **Action:** Manually verify and curate

```bash
# 1. Check PyPI manually
# Visit: https://pypi.org/project/setuptools/

# 2. Verify from source
# GitHub: https://github.com/pypa/setuptools
# LICENSE file shows: MIT

# 3. Add curation (in parent project .ort/curations.yml)
```

---

## Next Steps

### Daily Usage

**After initial setup, run this daily:**

```bash
#!/bin/bash
# daily-license-check.sh

# Re-run ORT analysis
ort analyze -i . -o ort-results/analyzer

# Check for license changes
python Advanced_License_Curation_Workflow/scripts/license_change_monitor.py --check \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
  --output license-changes-report.html

# Check policy compliance
python Advanced_License_Curation_Workflow/scripts/policy_checker.py \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --output policy-compliance-report.html

echo "✅ Daily license check complete!"
echo "📊 Reports:"
echo "  - policy-compliance-report.html"
echo "  - license-changes-report.html"
```

**Make executable:**
```bash
chmod +x daily-license-check.sh
```

**Run:**
```bash
./daily-license-check.sh
```

### CI/CD Integration

**See:** [../README.md#workflow-integration](../README.md#workflow-integration)

**GitHub Actions template:** `../.github/workflows/license-compliance.yml`

### Advanced Features

Once comfortable with basics, explore:

1. **Smart Curation Engine** - Automated decision making
2. **Compliance Dashboard** - Unified reporting
3. **Email/Slack Notifications** - Alert configuration
4. **Approval Workflows** - Conditional license handling

---

## Common Issues

### "ORT command not found"

**Solution:**
```bash
# Install ORT
ORT_VERSION="70.0.1"
wget https://github.com/oss-review-toolkit/ort/releases/download/${ORT_VERSION}/ort-${ORT_VERSION}.tgz
tar -xzf ort-${ORT_VERSION}.tgz
export PATH="${PWD}/ort-${ORT_VERSION}/bin:$PATH"

# Verify
ort --version
```

### "ModuleNotFoundError: No module named 'yaml'"

**Solution:**
```bash
pip install pyyaml
```

### "Policy file not found"

**Solution:**
```bash
# Use absolute path
python Advanced_License_Curation_Workflow/scripts/policy_checker.py \
  --policy "$(pwd)/Advanced_License_Curation_Workflow/config/company-policy.yml" \
  --ort-results ort-results/analyzer/analyzer-result.yml
```

---

## Checklist

After completing this quick start, you should have:

- [ ] Python 3.8+ installed
- [ ] pyyaml and requests packages installed
- [ ] ORT installed (or results available)
- [ ] Company policy configured
- [ ] First policy compliance report generated
- [ ] License change tracking initialized
- [ ] (Optional) Alternative packages found for forbidden licenses
- [ ] Daily check script created

---

## Getting Help

- **Documentation:** [README.md](../README.md)
- **Examples:** [../examples/](../examples/)
- **Issues:** Report at GitHub Issues
- **Email:** compliance@yourcompany.com

---

**Ready for production? See [../docs/DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**

*Happy License Curating! 🎉*
