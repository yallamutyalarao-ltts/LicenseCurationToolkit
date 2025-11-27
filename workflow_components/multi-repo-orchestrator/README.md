# 🎯 Multi-Repository ORT Orchestrator

**Automated workflow triggering for ORT (OSS Review Toolkit) analysis across multiple GitHub repositories.**

[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-blue?logo=github-actions)](https://github.com/features/actions)
[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Scenarios](#usage-scenarios)
- [How It Works](#how-it-works)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)
- [Best Practices](#best-practices)

---

## 🎯 Overview

This orchestrator workflow provides **centralized triggering** of ORT analysis workflows across multiple repositories. Instead of manually triggering each repository's workflow, you can trigger all of them with a single action.

**Key Benefits:**
- ⏰ Schedule ORT scans across all repositories at once
- 🔄 Synchronize analysis timing for consistent reporting
- 🎯 Selective execution (trigger specific repos only)
- 📊 Parallel execution with configurable concurrency
- 🚦 Fail-safe execution (one failure doesn't stop others)

**Perfect for:**
- Organizations with 5+ repositories needing regular ORT scans
- DevOps teams managing multiple projects
- Compliance officers scheduling regular audits
- Security teams coordinating vulnerability assessments

---

## ✨ Features

### **Automated Scheduling**
- 🕐 Daily execution at configurable time (default: 2 AM UTC)
- 📅 Customizable cron schedule
- 🎯 Manual trigger with selective repo filtering
- 🔄 Automatic retry on transient failures

### **Intelligent Execution**
- ⚡ Parallel execution (default: 3 concurrent repos)
- 🛡️ Fail-safe mode (continue on errors)
- 📝 Detailed execution logging
- 🔗 Direct links to triggered workflow runs

### **Flexible Configuration**
- 📋 Repository list management
- 🎚️ Concurrency control
- 🔀 Branch selection support
- 🎯 Selective execution via inputs

---

## 🚀 Quick Start

### **Step 1: Create Orchestrator Repository**

```bash
# Create a new repository for orchestration
# Name it something like: ort-orchestrator or license-orchestrator
# Initialize with README
```

### **Step 2: Copy Workflow File**

```bash
# Copy the workflow to your orchestrator repo
cp multi-repo-orchestrator/.github/workflows/trigger-ort-analysis.yml \
   /path/to/ort-orchestrator/.github/workflows/
```

### **Step 3: Configure Target Repositories**

Edit `.github/workflows/trigger-ort-analysis.yml`:

```yaml
# Lines 24-26: List all target repositories
matrix:
  repository:
    - your-org/repo1
    - your-org/repo2
    - your-org/repo3
    # Add more repositories here
```

**Also update the summary section (lines 99-102):**

```bash
repos=(
  "your-org/repo1"
  "your-org/repo2"
  "your-org/repo3"
)
```

### **Step 4: Create PAT Token**

1. Go to **GitHub Settings** → **Developer settings** → **Personal Access Tokens** → **Fine-grained tokens**
2. Click **Generate new token**
3. **Token name:** `ort-orchestrator-access`
4. **Expiration:** 90 days (or custom)
5. **Repository access:** Select all repositories you want to trigger
6. **Permissions:**
   - ✅ **Actions:** Read and write
   - ✅ **Contents:** Read-only (for workflow access)
   - ✅ **Metadata:** Read-only
7. Click **Generate token** and copy it

### **Step 5: Add Token to Repository**

1. Go to **Orchestrator Repository Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. **Name:** `PAT_TOKEN`
4. **Value:** Paste your token
5. Click **Add secret**

### **Step 6: Verify Workflow Configuration**

Check that target repositories have the ORT workflow:

```bash
# Each target repo should have this workflow file:
.github/workflows/action_ort_llm_workflow_deploy.yml

# Or whatever your ORT workflow is named
# Update line 59 if your workflow has a different name
```

### **Step 7: Run First Orchestration**

1. Go to **Actions** tab in orchestrator repo
2. Select **Multi-Repo ORT Orchestrator** workflow
3. Click **Run workflow**
4. **Optional:** Enter specific repos (comma-separated) or leave empty for all
5. Click **Run workflow**

**Monitor execution:**
- Each target repository will start its ORT workflow
- Check individual repo Actions tabs for progress
- View orchestrator summary for aggregated status

---

## ⚙️ Configuration

### **Target Repositories**

Edit `.github/workflows/trigger-ort-analysis.yml` in **TWO locations**:

**Location 1: Matrix strategy (lines 24-26)**
```yaml
matrix:
  repository:
    - arkawick/scipy
    - arkawick/numpy
    - arkawick/pandas
    - arkawick/scikit-learn
```

**Location 2: Summary generation (lines 99-102)**
```bash
repos=(
  "arkawick/scipy"
  "arkawick/numpy"
  "arkawick/pandas"
  "arkawick/scikit-learn"
)
```

**Format:** Always use `owner/repository` (not full URLs)

### **Execution Schedule**

Change the cron schedule (line 6):

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
    # Or:
    # - cron: '0 */6 * * *'  # Every 6 hours
    # - cron: '0 0 * * 1'    # Weekly on Monday
    # - cron: '0 0 1 * *'    # Monthly on 1st
```

**Timezone note:** Cron uses UTC. Adjust for your local timezone.

### **Concurrency Control**

Adjust parallel execution (line 28):

```yaml
strategy:
  max-parallel: 3  # Number of repos to analyze simultaneously
  # Options:
  # - 1: Sequential execution (slow but safe)
  # - 3: Balanced (recommended for most cases)
  # - 5: Fast (requires good API rate limits)
  # - 10: Very fast (for large organizations with high quotas)
```

### **Target Workflow Name**

If your ORT workflow has a different name (line 59):

```yaml
workflow_id: 'action_ort_llm_workflow_deploy.yml'
# Change to your workflow filename, examples:
# - 'ort-analysis.yml'
# - 'license-scan.yml'
# - 'compliance-check.yml'
```

### **Target Branch**

Specify which branch to trigger (line 60):

```yaml
ref: 'main'
# Or:
# - 'master'
# - 'develop'
# - 'production'
```

---

## 🎬 Usage Scenarios

### **Scenario 1: Daily Scheduled Scan**

**Use case:** Regular compliance audits every night

```yaml
# Default configuration (line 6)
schedule:
  - cron: '0 2 * * *'  # 2 AM UTC daily
```

**Result:**
- All repositories scanned automatically
- Results available by morning
- Consistent timing for trend analysis

---

### **Scenario 2: Manual All-Repo Trigger**

**Use case:** On-demand scan of all repositories

**Steps:**
1. Go to **Actions** tab
2. Select **Multi-Repo ORT Orchestrator**
3. Click **Run workflow**
4. Leave **repositories** input empty
5. Click **Run workflow**

**Result:**
- All configured repos triggered immediately
- Parallel execution based on max-parallel setting

---

### **Scenario 3: Selective Repository Trigger**

**Use case:** Scan only specific repositories after major changes

**Steps:**
1. Go to **Actions** tab
2. Select **Multi-Repo ORT Orchestrator**
3. Click **Run workflow**
4. Enter **repositories:** `scipy,numpy` (comma-separated repo names)
5. Click **Run workflow**

**Result:**
- Only scipy and numpy workflows triggered
- Other repos skipped
- Faster execution

---

### **Scenario 4: API-Based Trigger**

**Use case:** Integrate with external systems (CI/CD, ticketing, etc.)

```bash
# Trigger all repositories
curl -X POST \
  -H "Authorization: token YOUR_PAT_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/YOUR_ORG/ort-orchestrator/actions/workflows/trigger-ort-analysis.yml/dispatches \
  -d '{"ref":"main"}'

# Trigger specific repositories
curl -X POST \
  -H "Authorization: token YOUR_PAT_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/YOUR_ORG/ort-orchestrator/actions/workflows/trigger-ort-analysis.yml/dispatches \
  -d '{"ref":"main","inputs":{"repositories":"scipy,numpy"}}'
```

---

## 🔍 How It Works

### **Execution Flow**

```
┌─────────────────────────────────────┐
│  Orchestrator Workflow Triggered    │
│  (Schedule / Manual / API)          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Matrix Strategy Expansion          │
│  • scipy → Job 1                    │
│  • numpy → Job 2                    │
│  • pandas → Job 3                   │
│  • ... (up to max-parallel)         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Parallel Job Execution             │
│  ┌─────────┐ ┌─────────┐ ┌────────┐│
│  │ Job 1   │ │ Job 2   │ │ Job 3  ││
│  │ scipy   │ │ numpy   │ │ pandas ││
│  └────┬────┘ └────┬────┘ └────┬───┘│
└───────┼───────────┼──────────┼─────┘
        │           │          │
        ▼           ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Trigger  │ │ Trigger  │ │ Trigger  │
│ workflow │ │ workflow │ │ workflow │
│ in scipy │ │ in numpy │ │in pandas │
│   repo   │ │   repo   │ │   repo   │
└──────────┘ └──────────┘ └──────────┘
        │           │          │
        ▼           ▼          ▼
┌─────────────────────────────────────┐
│  Wait 10 seconds (rate limiting)    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Generate Execution Summary         │
│  • Total repos triggered            │
│  • Links to Actions tabs            │
│  • Dashboard link                   │
└─────────────────────────────────────┘
```

### **Key Components**

**1. Matrix Strategy (lines 21-28)**
```yaml
strategy:
  matrix:
    repository: [list of repos]
  fail-fast: false  # Continue even if one fails
  max-parallel: 3   # Execute 3 at a time
```

**2. GitHub Script Action (lines 32-78)**
- Parses repository path
- Checks selective execution filter
- Calls GitHub API to trigger workflow
- Handles errors with detailed logging

**3. Rate Limiting (lines 80-81)**
```yaml
- name: Wait between triggers
  run: sleep 10  # Avoid API throttling
```

**4. Summary Generation (lines 83-111)**
- Creates execution report
- Lists all triggered repositories
- Links to dashboard for results

---

## 🔧 Customization

### **Custom Workflow Detection**

If target repos have different ORT workflow names:

```yaml
# Option 1: Hardcode specific workflow
workflow_id: 'my-custom-ort-workflow.yml'

# Option 2: Use workflow dispatch event (requires workflow setup)
# In target repos, set workflow trigger:
on:
  workflow_dispatch:
    inputs:
      triggered_by:
        description: 'Orchestrator that triggered this'
        required: false
```

### **Branch Detection**

Auto-detect default branch instead of hardcoding:

```yaml
# Add before workflow trigger (line 54):
- name: Detect default branch
  id: branch
  run: |
    DEFAULT_BRANCH=$(gh api repos/${{ matrix.repository }} --jq .default_branch)
    echo "branch=$DEFAULT_BRANCH" >> $GITHUB_OUTPUT
  env:
    GH_TOKEN: ${{ secrets.PAT_TOKEN }}

# Update ref in trigger (line 60):
ref: ${{ steps.branch.outputs.branch }}
```

### **Retry Logic**

Add automatic retry for transient failures:

```yaml
# Add after line 78:
- name: Retry on failure
  if: failure()
  uses: actions/github-script@v7
  with:
    github-token: ${{ secrets.PAT_TOKEN }}
    script: |
      console.log('🔄 Retrying after 30 seconds...');
      await new Promise(resolve => setTimeout(resolve, 30000));
      // Retry logic here
```

### **Notification Integration**

Send notifications on completion:

```yaml
# Add at end of workflow:
- name: Send Slack notification
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "ORT Orchestration completed",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Status:* ${{ job.status }}\n*Repositories:* ${{ matrix.repository }}"
            }
          }
        ]
      }
```

---

## 🔥 Troubleshooting

### **Issue 1: "404 - Not Found" error**

**Symptom:**
```
❌ Failed to trigger owner/repo: Not Found
   → Possible causes:
      1. Workflow file 'action_ort_llm_workflow_deploy.yml' not found
```

**Solutions:**

1. **Verify workflow file exists in target repo:**
   ```bash
   # Check if file exists
   curl -H "Authorization: token YOUR_PAT" \
     https://api.github.com/repos/owner/repo/contents/.github/workflows/action_ort_llm_workflow_deploy.yml
   ```

2. **Check workflow filename (line 59):**
   ```yaml
   workflow_id: 'action_ort_llm_workflow_deploy.yml'  # Must match exactly
   ```

3. **Verify branch exists:**
   ```yaml
   ref: 'main'  # Change to 'master' if that's your default branch
   ```

---

### **Issue 2: "403 - Forbidden" error**

**Symptom:**
```
❌ Failed to trigger owner/repo: Forbidden
   → PAT token doesn't have 'workflow' permission
```

**Solution:**

1. **Update PAT token permissions:**
   - Go to GitHub Settings → Developer settings → PAT
   - Edit your token
   - Enable **Actions: Read and write** ✅
   - Save changes

2. **Update GitHub Secret:**
   - Repository Settings → Secrets → Actions
   - Delete old `PAT_TOKEN`
   - Create new one with updated token

---

### **Issue 3: Workflow not triggering automatically**

**Symptom:**
```
Scheduled workflow doesn't run at specified time
```

**Solutions:**

1. **Check cron syntax:**
   ```yaml
   # CORRECT:
   cron: '0 2 * * *'  # Quoted, space-separated

   # WRONG:
   cron: 0 2 * * *    # Unquoted
   ```

2. **Verify workflow is enabled:**
   - Actions tab → Select workflow
   - Check for "This workflow is disabled" banner
   - Click "Enable workflow" if needed

3. **Check repository activity:**
   - GitHub disables scheduled workflows in inactive repos
   - Make a commit to re-enable

---

### **Issue 4: Rate limiting errors**

**Symptom:**
```
❌ API rate limit exceeded
```

**Solutions:**

1. **Increase wait time between triggers (line 81):**
   ```yaml
   run: sleep 30  # Increase from 10 to 30 seconds
   ```

2. **Reduce concurrency (line 28):**
   ```yaml
   max-parallel: 2  # Reduce from 3 to 2
   ```

3. **Use GitHub App instead of PAT:**
   - Create GitHub App with Actions permissions
   - Use app authentication (higher rate limits)

---

### **Issue 5: Selective execution not working**

**Symptom:**
```
Entered 'repo1,repo2' but all repos triggered
```

**Solution:**

**Check input parsing logic (lines 44-51):**
```yaml
const requestedRepos = '${{ inputs.repositories }}';
if (requestedRepos) {
  const requestedList = requestedRepos.split(',').map(r => r.trim());
  // Must match EITHER short name OR full path
  if (!requestedList.includes(repo) && !requestedList.includes(repoPath)) {
    console.log(`⏭️ Skipping ${repo} - not in requested list`);
    return;
  }
}
```

**Input format options:**
```
# Short names (repo only):
scipy,numpy,pandas

# Full paths (owner/repo):
arkawick/scipy,arkawick/numpy

# Mixed (either format works):
scipy,arkawick/numpy
```

---

## 🚀 Advanced Usage

### **Multi-Environment Orchestration**

Trigger different branches for different environments:

```yaml
# Add environment input
workflow_dispatch:
  inputs:
    environment:
      description: 'Target environment'
      required: false
      type: choice
      options:
        - development
        - staging
        - production

# Use in trigger
ref: ${{ inputs.environment || 'main' }}
```

### **Conditional Execution**

Trigger only if certain conditions are met:

```yaml
# Add before trigger step
- name: Check if trigger needed
  id: check
  run: |
    # Example: Check if it's a weekday
    DAY=$(date +%u)
    if [ $DAY -le 5 ]; then
      echo "trigger=true" >> $GITHUB_OUTPUT
    else
      echo "trigger=false" >> $GITHUB_OUTPUT
    fi

# Update trigger step
- name: Trigger ORT workflow
  if: steps.check.outputs.trigger == 'true'
  uses: actions/github-script@v7
  # ... rest of config
```

### **Dynamic Repository Discovery**

Auto-discover repositories with ORT workflows:

```yaml
# Add before matrix strategy
- name: Discover ORT repositories
  id: discover
  uses: actions/github-script@v7
  with:
    github-token: ${{ secrets.PAT_TOKEN }}
    script: |
      const org = 'your-org';
      const repos = await github.paginate(github.rest.repos.listForOrg, {
        org,
        type: 'all'
      });

      const ortRepos = [];
      for (const repo of repos) {
        try {
          await github.rest.repos.getContent({
            owner: org,
            repo: repo.name,
            path: '.github/workflows/action_ort_llm_workflow_deploy.yml'
          });
          ortRepos.push(`${org}/${repo.name}`);
        } catch {}
      }

      core.setOutput('repos', JSON.stringify(ortRepos));

# Use discovered repos in matrix
matrix:
  repository: ${{ fromJson(steps.discover.outputs.repos) }}
```

---

## 📊 Best Practices

### **✅ DO**

1. **Use descriptive commit messages:**
   ```bash
   git commit -m "chore: Add tensorflow to ORT orchestration

   - Added arkawick/tensorflow to matrix
   - Updated summary generation
   - Refs: COMPLIANCE-123"
   ```

2. **Keep repository lists synchronized:**
   - Update BOTH matrix and summary sections
   - Consider using reusable config file

3. **Monitor API rate limits:**
   - Check usage: Settings → Developer settings → PAT → Usage
   - Stay well below limits

4. **Test with small batches first:**
   ```yaml
   # Start with 1-2 repos
   matrix:
    repository:
      - your-org/test-repo1
      - your-org/test-repo2

   # Then scale up after verification
   ```

5. **Use fail-fast: false:**
   ```yaml
   strategy:
     fail-fast: false  # Don't stop all jobs if one fails
   ```

### **❌ DON'T**

1. **Don't use root PAT tokens:**
   - Use fine-grained tokens with minimal permissions
   - Regularly rotate tokens

2. **Don't set max-parallel too high:**
   ```yaml
   max-parallel: 20  # ❌ Can hit rate limits
   max-parallel: 3   # ✅ Balanced approach
   ```

3. **Don't hardcode sensitive data:**
   ```yaml
   # ❌ WRONG
   github-token: ghp_abc123...

   # ✅ CORRECT
   github-token: ${{ secrets.PAT_TOKEN }}
   ```

4. **Don't skip rate limit delays:**
   ```yaml
   # ❌ WRONG
   # run: sleep 10  # Commented out

   # ✅ CORRECT
   run: sleep 10  # Prevents API throttling
   ```

5. **Don't ignore error logs:**
   - Review failed runs immediately
   - Check triggered repos' Actions tabs
   - Investigate 404/403 errors

---

## 🔗 Integration with Dashboard

This orchestrator works perfectly with the **Multi-Repo Dashboard**:

```
┌─────────────────────────────────┐
│  Multi-Repo ORT Orchestrator    │
│  (This component)               │
│  • Triggers workflows           │
│  • Schedules executions         │
└──────────────┬──────────────────┘
               │ Triggers
               ▼
┌─────────────────────────────────┐
│  Target Repository Workflows    │
│  • action_ort_llm_workflow...   │
│  • Runs ORT analysis            │
│  • Generates reports            │
│  • Deploys to GitHub Pages      │
└──────────────┬──────────────────┘
               │ Results stored
               ▼
┌─────────────────────────────────┐
│  Multi-Repo Dashboard           │
│  (Separate component)           │
│  • Collects results             │
│  • Displays aggregated stats    │
│  • Shows compliance scores      │
└─────────────────────────────────┘
```

**Setup both for complete solution:**
1. Deploy this orchestrator → Triggers scans
2. Deploy dashboard → Displays results
3. Schedule orchestrator before dashboard (offset by 30+ minutes)

Example cron schedules:
```yaml
# Orchestrator (trigger scans)
cron: '0 2 * * *'  # 2:00 AM

# Dashboard (collect results)
cron: '0 3 * * *'  # 3:00 AM (1 hour later)
```

---

## 📚 Additional Resources

**Related Documentation:**
- [Multi-Repo Dashboard](../multi-repo-dashboard/README.md) - Result aggregation
- [Main Workflow Guide](../README.md) - Individual repository workflow
- [Policy Configuration](../docs/POLICY_GUIDE.md) - License policy setup
- [Deployment Guide](../DEPLOYMENT_GUIDE.md) - Production deployment

**GitHub Actions Documentation:**
- [Workflow Dispatch](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_dispatch)
- [Matrix Strategy](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs)
- [GitHub Script](https://github.com/actions/github-script)

---

## 🆘 Getting Help

**Troubleshooting steps:**
1. Check workflow run logs in Actions tab
2. Verify PAT token permissions
3. Confirm target workflow files exist
4. Test with single repository first
5. Review error messages in logs

**Common error patterns:**
- `404` → Workflow file or branch not found
- `403` → Insufficient PAT permissions
- `422` → Invalid input parameters
- `429` → Rate limit exceeded

**Still stuck?**
- Review logs in target repository Actions tabs
- Check [GitHub Actions status](https://www.githubstatus.com/)
- Verify API rate limits haven't been exceeded

---

## 📊 Workflow Summary

**Purpose:** Centralized triggering of ORT workflows across multiple repositories

**Triggers:**
- ⏰ Daily at 2 AM UTC (configurable)
- 🎯 Manual execution (all or selective repos)
- 🔌 API-based trigger

**Execution:**
- ⚡ Parallel with configurable concurrency
- 🛡️ Fail-safe (continues on errors)
- 🔄 10-second delay between triggers
- 📝 Detailed logging and error handling

**Output:**
- ✅ Triggered workflows in target repositories
- 📋 Execution summary with repository links
- 🔗 Link to dashboard for aggregated results

---

## ✅ Quick Verification

After setup, verify everything works:

1. **Manual trigger test:**
   ```
   Actions → Multi-Repo ORT Orchestrator → Run workflow
   ```

2. **Check orchestrator logs:**
   ```
   Look for: "✅ Successfully triggered for owner/repo"
   ```

3. **Verify target repos:**
   ```
   Go to each target repo → Actions tab
   Should see new workflow run starting
   ```

4. **Review summary:**
   ```
   Orchestrator run → Summary tab
   Check repository links
   ```

**Expected results:**
- ✅ All target repos show new workflow runs
- ✅ No 404 or 403 errors in logs
- ✅ Summary shows all triggered repositories
- ✅ Dashboard (if configured) shows updated results

---

## 🎉 You're All Set!

Your multi-repository orchestration is now configured with:
- ✅ Centralized workflow triggering
- ✅ Scheduled automatic execution
- ✅ Parallel processing with concurrency control
- ✅ Fail-safe error handling
- ✅ Detailed execution reporting

**Time invested:** ~20 minutes
**Repos managed:** Unlimited
**Manual triggers saved:** Hours per week

---

**Made with ❤️ for DevOps and Compliance teams**

*Last Updated: 2025-01-27*
