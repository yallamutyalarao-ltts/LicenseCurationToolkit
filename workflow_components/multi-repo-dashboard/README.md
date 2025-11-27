# 🏢 Multi-Repository ORT Dashboard

**Centralized monitoring dashboard for ORT (OSS Review Toolkit) analysis across multiple GitHub repositories.**

[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue?logo=github)](https://github.com/features/pages)
[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Dashboard UI](#dashboard-ui)
- [How It Works](#how-it-works)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

---

## 🎯 Overview

This repository provides a **centralized dashboard** that aggregates ORT analysis results from multiple repositories. Instead of checking each repository individually, you get a unified view of:

- ✅ Latest scan status for all repos
- ⚠️ Vulnerability counts
- 📊 Compliance metrics
- 🔗 Direct links to detailed reports

**Perfect for:**
- Organizations with 5+ repositories running ORT analysis
- DevOps teams monitoring license compliance across projects
- Security teams tracking vulnerabilities
- Compliance officers needing executive dashboards

---

## ✨ Features

### **Automated Data Collection**
- 🤖 Runs every 6 hours automatically
- 📡 Fetches latest workflow results via GitHub API
- 🔍 Detects ORT workflows by name pattern
- 📦 Analyzes artifacts and vulnerability reports

### **Beautiful Dashboard**
- 🎨 Modern, responsive UI with gradient design
- 📊 Summary statistics (repos, successes, issues)
- 📈 Real-time status badges (success/failure/error)
- 🔗 One-click access to detailed reports
- 📱 Mobile-friendly layout

### **Intelligent Monitoring**
- ⏰ Shows hours since last scan
- 🚨 Highlights repositories with issues
- 📋 Links to GitHub Pages reports
- 🔍 Direct links to workflow run details

---

## 🚀 Quick Start

### **Step 1: Create Dashboard Repository**

```bash
# Create a new repository for the dashboard
# Name it something like: ort-dashboard or license-dashboard
# Initialize with README
```

### **Step 2: Copy Workflow File**

```bash
# Copy the workflow to your new dashboard repo
cp multi-repo-dashboard/.github/workflows/generate-dashboard.yml \
   /path/to/ort-dashboard/.github/workflows/
```

### **Step 3: Configure Repositories**

Edit `.github/workflows/generate-dashboard.yml`:

```yaml
# Line 40-43: List all your target repositories
const repos = [
  'your-org/repo1',
  'your-org/repo2',
  'your-org/repo3',
  // Add more repositories here
];
```

### **Step 4: Create PAT Token**

1. Go to **GitHub Settings** → **Developer settings** → **Personal Access Tokens** → **Fine-grained tokens**
2. Click **Generate new token**
3. **Token name:** `ort-dashboard-access`
4. **Expiration:** 90 days (or custom)
5. **Repository access:** Select repositories to monitor
6. **Permissions:**
   - ✅ **Actions:** Read-only
   - ✅ **Metadata:** Read-only
7. Click **Generate token** and copy it

### **Step 5: Add Token to Repository**

1. Go to **Dashboard Repository Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. **Name:** `PAT_TOKEN`
4. **Value:** Paste your token
5. Click **Add secret**

### **Step 6: Enable GitHub Pages**

1. Go to **Repository Settings** → **Pages**
2. **Source:** Deploy from a branch
3. **Branch:** Select `gh-pages` (will be created automatically)
4. Click **Save**

### **Step 7: Run Workflow**

1. Go to **Actions** tab
2. Select **Generate ORT Dashboard** workflow
3. Click **Run workflow** → **Run workflow**
4. Wait 1-2 minutes for completion

**Your dashboard will be available at:**
```
https://<your-org>.github.io/<dashboard-repo-name>/
```

Example: `https://arkawick.github.io/ort-dashboard/`

---

## ⚙️ Configuration

### **Monitored Repositories**

Edit `.github/workflows/generate-dashboard.yml` (lines 40-43):

```javascript
const repos = [
  'organization/scipy',
  'organization/numpy',
  'organization/pandas',
  'organization/scikit-learn',
  'organization/matplotlib'
];
```

**Format:** Always use `owner/repository` format (not full URLs)

### **Update Schedule**

Change the cron schedule (line 6):

```yaml
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
    # Or:
    # - cron: '0 */2 * * *'  # Every 2 hours
    # - cron: '0 0 * * *'    # Once daily at midnight
    # - cron: '0 0 * * 1'    # Once weekly on Monday
```

---

