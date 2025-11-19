# Examples

This directory contains example usage scenarios and test data.

---

## 📁 Contents

- `test-ort-result.yml` - Sample ORT analyzer result for testing
- `example-workflow.sh` - Complete workflow example script
- `scenario-*.md` - Real-world scenario walkthroughs

---

## 🎯 Quick Examples

### Example 1: Check Policy Compliance

```bash
python ../scripts/policy_checker.py \
  --policy ../config/company-policy.yml \
  --ort-results test-ort-result.yml \
  --output test-policy-report.html
```

### Example 2: Find Alternatives for GPL Package

```bash
python ../scripts/alternative_package_finder.py \
  --package "pycutest" \
  --type "PyPI" \
  --forbidden-license "GPL-3.0-or-later" \
  --policy ../config/company-policy.yml \
  --output test-alternatives.html
```

### Example 3: Initialize License Tracking

```bash
python ../scripts/license_change_monitor.py --init \
  --ort-results test-ort-result.yml \
  --history test-license-history.json
```

### Example 4: Check for License Changes

```bash
# After some time passes or dependencies change...

python ../scripts/license_change_monitor.py --check \
  --ort-results test-ort-result-new.yml \
  --policy ../config/company-policy.yml \
  --history test-license-history.json \
  --output test-changes-report.html
```

---

## 📖 Scenario Walkthroughs

### Scenario 1: New Project Setup

**Situation:** Starting a new Python project, want to ensure compliance from day 1.

**Steps:**

```bash
# 1. Initialize project
mkdir my-new-project
cd my-new-project
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install requests numpy pandas

# 3. Copy Advanced_License_Curation_Workflow
cp -r ../Advanced_License_Curation_Workflow .

# 4. Run ORT analysis
ort analyze -i . -o ort-results/analyzer

# 5. Check compliance
python Advanced_License_Curation_Workflow/scripts/policy_checker.py \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --output policy-report.html

# 6. Initialize tracking
python Advanced_License_Curation_Workflow/scripts/license_change_monitor.py --init \
  --ort-results ort-results/analyzer/analyzer-result.yml

# 7. Review report
open policy-report.html
```

---

### Scenario 2: Dealing with Forbidden License

**Situation:** Package `some-lib` has GPL-3.0 license, which is forbidden by policy.

**Steps:**

```bash
# 1. Identify forbidden package (from policy report)
# Package: some-lib
# License: GPL-3.0-only
# Status: FORBIDDEN

# 2. Find alternatives
python Advanced_License_Curation_Workflow/scripts/alternative_package_finder.py \
  --package "some-lib" \
  --type "PyPI" \
  --forbidden-license "GPL-3.0-only" \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
  --output alternatives-some-lib.html

# 3. Review alternatives
open alternatives-some-lib.html

# Alternatives found:
#   1. alternative-lib (MIT) - Score: 0.95
#   2. replacement-lib (Apache-2.0) - Score: 0.88
#   3. libre-lib (BSD-3-Clause) - Score: 0.82

# 4. Choose best alternative (alternative-lib)
# Update requirements.txt:
#   - some-lib==1.0.0  # Remove
#   + alternative-lib==2.3.0  # Add

# 5. Install new dependency
pip uninstall some-lib
pip install alternative-lib

# 6. Update code (if API changed)
# Replace imports:
#   - from some_lib import func
#   + from alternative_lib import func

# 7. Test thoroughly
pytest

# 8. Re-run compliance check
ort analyze -i . -o ort-results/analyzer
python Advanced_License_Curation_Workflow/scripts/policy_checker.py \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --output policy-report-fixed.html

# 9. Verify: Forbidden count should be 0
```

---

### Scenario 3: License Suddenly Changed

**Situation:** Dependency `requests` upgraded from 2.28.0 (Apache-2.0) to 2.29.0 (GPL-3.0)

**Detection:**

```bash
# Daily CI/CD run detects change

python Advanced_License_Curation_Workflow/scripts/license_change_monitor.py --check \
  --ort-results ort-results/analyzer/analyzer-result.yml \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
  --output license-changes-report.html

# Output:
# ⚠️ LICENSE CHANGE DETECTED
# Package: requests
# Previous: Apache-2.0
# Current: GPL-3.0-only
# Severity: CRITICAL
# Risk: Permissive to Copyleft
```

**Response:**

```bash
# 1. Open alert report
open license-changes-report.html

# 2. Follow recommended actions:
# ⛔ IMMEDIATE ACTION REQUIRED
# 1. Stop using this package version immediately
# 2. Review legal implications with compliance team
# 3. Consider reverting to previous version or finding alternative
# 4. Update package dependencies to pin to safe version

# 3. Pin to previous version
# Update requirements.txt:
#   requests==2.28.0  # Pin to safe version

# 4. Or find alternative (if really GPL now)
python Advanced_License_Curation_Workflow/scripts/alternative_package_finder.py \
  --package "requests" \
  --type "PyPI" \
  --forbidden-license "GPL-3.0-only" \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml

# 5. Investigate why license changed
# - Check PyPI: https://pypi.org/project/requests/
# - Check GitHub: https://github.com/psf/requests
# - Contact maintainers if suspicious

# 6. Document incident
# Add to .ort/audit-log.json

# 7. Re-run check to verify
ort analyze -i . -o ort-results/analyzer
python Advanced_License_Curation_Workflow/scripts/license_change_monitor.py --check \
  --ort-results ort-results/analyzer/analyzer-result.yml
```

---

### Scenario 4: Conditional License Approval

**Situation:** Package `ml-toolkit` has LGPL-3.0, which requires approval.

**Steps:**

```bash
# 1. Policy check identifies conditional package
# Package: ml-toolkit
# License: LGPL-3.0-only
# Status: CONDITIONAL
# Approval Required: Yes
# Approvers: legal@company.com, compliance@company.com

# 2. Prepare approval request
cat > approval-request-ml-toolkit.md <<EOF
## License Approval Request

**Package:** ml-toolkit
**Version:** 3.2.1
**License:** LGPL-3.0-only
**Category:** Weak Copyleft

**Use Case:** Machine learning data preprocessing in internal research tool

**Deployment:** Internal only, not customer-facing

**Linking:** Dynamic linking (Python import, not compiled)

**Compliance Requirements:**
- Include original LGPL-3.0 license text
- Document usage in NOTICE file
- If we modify ml-toolkit source, release modifications under LGPL-3.0

**Risk Assessment:** LOW
- Internal tool only
- Dynamic linking (Python)
- No distribution to customers

**Alternatives Evaluated:**
1. apache-ml (Apache-2.0) - Missing required feature X
2. mit-preprocessor (MIT) - Performance 50% slower
3. ml-toolkit (LGPL-3.0) - Best fit for requirements

**Recommendation:** APPROVE with conditions

**Requested by:** Engineering Team
**Date:** 2025-01-16
EOF

# 3. Send for approval
# Email to legal@company.com, compliance@company.com
# Attach: approval-request-ml-toolkit.md, policy-compliance-report.html

# 4. After approval received:
# Document in .ort/curations.yml

cat >> .ort/curations.yml <<EOF
  - id: "PyPI::ml-toolkit:3.2.1"
    curations:
      comment: |
        License: LGPL-3.0-only
        Status: APPROVED (Conditional)
        Approved by: legal@company.com on 2025-01-16
        Approval ticket: LEGAL-12345
        Conditions:
          - Internal use only
          - Include LGPL-3.0 license text in deployment
          - Document in NOTICE file
        Rationale: Required for ML preprocessing, no suitable alternatives
      concluded_license: "LGPL-3.0-only"
      declared_license_mapping:
        "LGPL-3.0-only": "LGPL-3.0-only"
EOF

# 5. Re-run compliance check to verify
ort analyze -i . -o ort-results/analyzer
python Advanced_License_Curation_Workflow/scripts/policy_checker.py \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml

# Package should now show as APPROVED with conditions
```

---

### Scenario 5: Unknown License Research

**Situation:** Package `obscure-lib` has "NOASSERTION" license.

**Steps:**

```bash
# 1. Manual research process

# Step 1: Check PyPI
# Visit: https://pypi.org/project/obscure-lib/
# License field: "UNKNOWN" - not helpful

# Step 2: Check package classifiers
pip show obscure-lib
# Classifiers: None listed

# Step 3: Download and inspect source
pip download obscure-lib --no-deps
tar -xzf obscure-lib-1.0.0.tar.gz
cd obscure-lib-1.0.0

# Step 4: Check for LICENSE file
ls -la
# Found: LICENSE.txt

cat LICENSE.txt
# Shows: MIT License

# Step 5: Check source file headers
head -n 20 obscure_lib/__init__.py
# Header shows: Licensed under MIT

# Step 6: Check setup.py/pyproject.toml
cat setup.py | grep -i license
# license='MIT'

# Step 7: Check GitHub repository
# URL from PyPI: https://github.com/user/obscure-lib
# LICENSE file on GitHub: MIT

# 2. Document findings

cat > research-obscure-lib.md <<EOF
## License Research: obscure-lib

**Package:** obscure-lib 1.0.0
**Research Date:** 2025-01-16
**Researcher:** Your Name

**Sources Checked:**
- PyPI page: UNKNOWN (metadata incorrect)
- LICENSE.txt in source: MIT License
- Source file headers: MIT
- setup.py: license='MIT'
- GitHub repository: MIT (https://github.com/user/obscure-lib/blob/main/LICENSE)

**Conclusion:** MIT License

**Confidence:** HIGH (multiple consistent sources)

**Recommendation:** Add curation to mark as MIT

**Evidence:**
- [Screenshot of GitHub LICENSE]
- [Copy of LICENSE.txt from package]
EOF

# 3. Add curation

cat >> .ort/curations.yml <<EOF
  - id: "PyPI::obscure-lib:1.0.0"
    curations:
      comment: |
        License: MIT
        Verified by: Your Name on 2025-01-16
        Original declared: NOASSERTION (incorrect metadata)
        Evidence:
          - LICENSE.txt in source distribution: MIT License
          - GitHub repository: https://github.com/user/obscure-lib/blob/main/LICENSE
          - Source file headers: MIT
          - setup.py: license='MIT'
        Research document: research-obscure-lib.md
      concluded_license: "MIT"
      declared_license_mapping:
        "NOASSERTION": "MIT"
      source_artifact_url: "https://pypi.org/packages/source/o/obscure-lib/obscure-lib-1.0.0.tar.gz"
      vcs:
        type: "Git"
        url: "https://github.com/user/obscure-lib.git"
        revision: "v1.0.0"
EOF

# 4. Verify curation
ort analyze -i . -o ort-results/analyzer
python Advanced_License_Curation_Workflow/scripts/policy_checker.py \
  --policy Advanced_License_Curation_Workflow/config/company-policy.yml \
  --ort-results ort-results/analyzer/analyzer-result.yml

# Package should now show as MIT (APPROVED)
```

---

## 🧪 Testing the Workflow

**Use provided test data:**

```bash
cd examples/

# Test policy checker
python ../scripts/policy_checker.py \
  --policy ../config/company-policy.yml \
  --ort-results test-ort-result.yml \
  --output test-output/policy-report.html

# Expected output:
# - Some approved packages (MIT, Apache-2.0)
# - Some conditional (LGPL-3.0)
# - Some forbidden (GPL-3.0)
# - Some unknown (NOASSERTION)
```

---

## 📚 More Resources

- [Main README](../README.md)
- [Quick Start Guide](../docs/QUICK_START.md)
- [Policy Configuration Guide](../docs/POLICY_GUIDE.md)
- [Troubleshooting](../README.md#troubleshooting)

---

**Need more examples? Request at:** examples-request@yourcompany.com
