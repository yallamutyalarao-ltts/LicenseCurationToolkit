# Quick Setup Guide

> Get started with Advanced License Curation in 15 minutes

---

## 🚀 Prerequisites Checklist

- [ ] GitHub repository with code to analyze
- [ ] Python 3.11+ installed locally
- [ ] Access to GitHub Actions (for CI/CD)
- [ ] (Optional) Azure OpenAI account for AI features

---

## ⏱️ 15-Minute Setup

### Step 1: Copy Files (2 minutes)

```bash
# Navigate to your repository
cd /path/to/your/repository

# Create workflow directory
mkdir -p .github/workflows

# Copy workflow components
# Option A: Clone from source
git clone https://github.com/your-org/LicenseCurationTool temp-license-tool
cp temp-license-tool/License_Curation/workflow_components/advanced-integrated-workflow.yml .github/workflows/
cp -r temp-license-tool/License_Curation/workflow_components .
rm -rf temp-license-tool

# Option B: Download and extract manually
# Download workflow_components/ folder and copy to your repository
```

**Expected structure:**
```
your-repository/
├── .github/
│   └── workflows/
│       └── advanced-integrated-workflow.yml
├── workflow_components/
│   ├── scripts/
│   │   ├── policy_checker.py
│   │   ├── license_change_monitor.py
│   │   └── alternative_package_finder.py
│   ├── config/
│   │   └── company-policy.yml
│   ├── docs/
│   ├── requirements.txt
│   └── README.md
├── your-source-code/
└── ...
```

---

### Step 2: Configure Company Policy (5 minutes)

```bash
# Edit the policy file
nano workflow_components/config/company-policy.yml
# Or use your favorite editor
```

**Minimum required changes:**

```yaml
company_license_policy:
  company_name: "Your Company Name"  # ← CHANGE THIS

  # Licenses you ALLOW
  approved_licenses:
    permissive:
      licenses:
        - "MIT"
        - "Apache-2.0"
        - "BSD-3-Clause"
        # Add more as needed

  # Licenses you FORBID
  forbidden_licenses:
    proprietary_restricted:
      licenses:
        - "SSPL-1.0"
        - "GPL-3.0-only"  # ← CUSTOMIZE THIS LIST
        - "Proprietary"
```

**Common configurations by company type:**

**For Proprietary Software Companies:**
```yaml
forbidden_licenses:
  strong_copyleft:
    licenses:
      - "GPL-2.0-only"
      - "GPL-2.0-or-later"
      - "GPL-3.0-only"
      - "GPL-3.0-or-later"
      - "AGPL-3.0-only"
      - "AGPL-3.0-or-later"
      - "SSPL-1.0"
```

**For Open Source Projects:**
```yaml
approved_licenses:
  permissive:
    licenses:
      - "MIT"
      - "Apache-2.0"
      - "BSD-3-Clause"
  weak_copyleft:
    licenses:
      - "LGPL-2.1-or-later"
      - "LGPL-3.0-or-later"
      - "MPL-2.0"
  strong_copyleft:
    licenses:
      - "GPL-3.0-or-later"  # OK for open source
```

---

### Step 3: (Optional) Set Up Azure OpenAI (3 minutes)

**For AI-powered features only. Skip if not needed.**

1. **Get Azure OpenAI credentials:**
   - Azure Portal → Your OpenAI Resource → Keys and Endpoint
   - Copy:
     - API Key
     - Endpoint (e.g., `https://your-resource.openai.azure.com/`)
     - Deployment Name (from Model deployments page)

2. **Add GitHub Secrets:**
   ```
   Repository → Settings → Secrets and variables → Actions → New repository secret
   ```

   Add three secrets:
   - **Name:** `AZURE_OPENAI_API_KEY`
     **Value:** `your-api-key-here`

   - **Name:** `AZURE_OPENAI_ENDPOINT`
     **Value:** `https://your-resource.openai.azure.com/`

   - **Name:** `AZURE_OPENAI_MODEL`
     **Value:** `your-deployment-name` (e.g., `gpt-4o-mini`)

**Cost estimate:** ~$0.20-$0.33 per workflow run, ~$6-$10/month for daily runs

**What happens without AI?**
- Policy checking ✅ Still works
- License change monitoring ✅ Still works
- Alternative package finder ✅ Still works
- AI curation reports ❌ Skipped (not critical)

---

### Step 4: Commit and Push (2 minutes)

```bash
# Add files
git add .github/workflows/advanced-integrated-workflow.yml
git add workflow_components/

# Commit
git commit -m "Add advanced license curation workflow

- Policy-based license enforcement
- License change monitoring
- Alternative package finder
- Multi-source license detection (ORT + PyPI + ScanCode + AI)"

# Push
git push origin main
```

---

### Step 5: Verify Workflow (3 minutes)

1. **Go to GitHub:**
   ```
   Your Repository → Actions
   ```

2. **Find workflow:**
   - Look for "Advanced ORT License Curation with Policy Enforcement"
   - Should trigger automatically on push

3. **Watch first run:**
   - Click on the running workflow
   - Monitor progress (takes ~10-20 minutes first time)

4. **Check results:**
   - Once complete, click "Summary"
   - View:
     - ✅ Compliance Score
     - ✅ Policy violations
     - ✅ License changes
     - ✅ Forbidden packages (if any)

---

## ✅ Verification Checklist

After first workflow run:

- [ ] Workflow completed successfully (green checkmark)
- [ ] Policy compliance report generated
- [ ] No forbidden packages detected (or alternatives suggested)
- [ ] GitHub Pages deployed (if enabled)
- [ ] Artifacts uploaded (download to verify)

---

## 🎯 Quick Wins

### Win #1: Find Forbidden Packages Instantly

**Before:**
```
Manual review of 500+ dependencies
Legal team consult for each package
Weeks to identify GPL violations
```

**After:**
```
✅ Automated scan: 5 minutes
❌ 2 forbidden packages found:
   - pycutest (GPL-3.0-or-later)
   - mongodb-driver (SSPL-1.0)

🔄 Alternatives suggested:
   - cutest-alternative (MIT) - Score: 0.92
   - pymongo-alternative (Apache-2.0) - Score: 0.88
```

---

### Win #2: Catch License Changes Automatically

**Before:**
```
Dependency updates without license review
Surprise GPL in production
Compliance violations discovered late
```

**After:**
```
⛔ CRITICAL LICENSE CHANGE DETECTED!
   requests 2.28.0: MIT → GPL-3.0-only

Recommended Actions:
   1. Pin to requests==2.27.1 (MIT)
   2. Find alternative package
   3. Contact maintainer

Build FAILED to prevent deployment
```

---

### Win #3: Compliance Score Tracking

**Before:**
```
Unknown compliance status
Manual spreadsheets
No visibility for stakeholders
```

**After:**
```
📊 Compliance Score: 84%
   ✅ Approved:    42 packages
   ⚠️  Conditional: 5 packages (need approval)
   ❌ Forbidden:   2 packages (URGENT)
   ❓ Unknown:     1 package (research needed)

📈 Trend: ↑ 4% from last scan
```

---

## 🔥 Common First-Run Issues

### Issue 1: Workflow fails immediately

**Symptom:**
```
Error: ENOENT: no such file or directory
```

**Solution:**
```bash
# Check file structure
ls -la .github/workflows/advanced-integrated-workflow.yml
ls -la workflow_components/

# Files must be in correct locations
```

---

### Issue 2: Policy file not found

**Symptom:**
```
❌ Policy file not found: workflow_components/config/company-policy.yml
```

**Solution:**
```bash
# Verify policy file exists
cat workflow_components/config/company-policy.yml

# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('workflow_components/config/company-policy.yml'))"
```

---

### Issue 3: Forbidden packages detected (expected!)

**Symptom:**
```
❌ FORBIDDEN PACKAGES DETECTED!
Build failed
```

**Solution:**
```
This is correct behavior! The workflow is protecting you.

Options:
1. View alternatives report → Replace package
2. Request exception from legal team → Update policy
3. Pin to previous version → Update dependencies

DO NOT disable the check without approval!
```

---

### Issue 4: Azure OpenAI errors (if using AI)

**Symptom:**
```
⚠️  AZURE_OPENAI_API_KEY not set, skipping AI report...
```

**Solution:**
```
This is OK if you don't need AI features!

To enable AI:
1. Check GitHub Secrets configured correctly
2. Verify endpoint format: https://your-resource.openai.azure.com/
3. Test with curl (see README.md Troubleshooting)

Workflow still generates all non-AI reports ✅
```

---

## 📚 Next Steps

### Day 1: Review Results
- [ ] Review policy compliance report
- [ ] Check for forbidden packages
- [ ] Review alternatives for forbidden packages
- [ ] Document any policy exceptions needed

### Week 1: Integrate with Team
- [ ] Share reports with legal/compliance team
- [ ] Set up approval workflow for conditional licenses
- [ ] Document replacement decisions
- [ ] Train team on workflow

### Month 1: Optimize
- [ ] Review and update company policy
- [ ] Fine-tune alternative package rankings
- [ ] Set up automated PR comments
- [ ] Enable GitHub Pages dashboard

---

## 🆘 Getting Help

**Check documentation:**
1. [README.md](../README.md) - Complete guide
2. [POLICY_GUIDE.md](POLICY_GUIDE.md) - Policy configuration
3. [WORKFLOW_DIAGRAM.md](WORKFLOW_DIAGRAM.md) - Architecture details
4. [../CLAUDE.md](../../CLAUDE.md) - System documentation

**Still stuck?**
- GitHub Issues: Report bugs/feature requests
- Email: compliance@yourcompany.com
- Slack: #license-compliance (if available)

---

## 🎉 Success!

You're now running advanced license curation with:
- ✅ Automated policy enforcement
- ✅ License change detection
- ✅ Alternative package recommendations
- ✅ Multi-source license detection
- ✅ AI-powered conflict resolution

**Time invested:** 15 minutes
**Time saved:** Hours per week
**Compliance risk:** Significantly reduced

---

**Made with ❤️ for software compliance teams**

*Last Updated: 2025-01-19*
