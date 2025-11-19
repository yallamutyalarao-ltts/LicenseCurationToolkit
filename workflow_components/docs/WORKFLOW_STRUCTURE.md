# Workflow Structure Overview

> Detailed breakdown of the Advanced License Curation Workflow architecture

---

## 📋 Table of Contents

- [Folder Structure](#folder-structure)
- [Workflow Stages](#workflow-stages)
- [Data Flow](#data-flow)
- [Integration Points](#integration-points)
- [File Outputs](#file-outputs)

---

## 📁 Folder Structure

```
your-repository/
├── .github/
│   └── workflows/
│       └── advanced-integrated-workflow.yml   # Main workflow file
│
├── workflow_components/                       # Imported from LicenseCurationTool
│   ├── scripts/
│   │   ├── policy_checker.py                  # Stage 2: Policy enforcement
│   │   ├── license_change_monitor.py          # Stage 3: Change tracking
│   │   └── alternative_package_finder.py      # Stage 4: Alternative search
│   ├── config/
│   │   └── company-policy.yml                 # Policy database
│   ├── docs/
│   │   ├── QUICK_SETUP.md                     # Getting started guide
│   │   └── WORKFLOW_STRUCTURE.md              # This file
│   ├── requirements.txt                       # Python dependencies
│   └── README.md                              # Main documentation
│
├── .ort/                                      # Created during workflow
│   └── license-history.json                   # License change tracking DB
│
├── ort-results/                               # Created during workflow
│   ├── analyzer/
│   │   └── analyzer-result.yml                # ORT analysis output
│   ├── advisor/
│   │   └── advise-result.yml                  # Vulnerability data
│   └── reporter/
│       ├── bom.spdx.yml                       # Original SPDX
│       ├── bom.cyclonedx.json                 # CycloneDX SBOM
│       ├── scan-report-web-app.html           # Interactive report
│       └── scan-report.html                   # Static report
│
├── policy-reports/                            # Created during workflow
│   ├── policy-compliance-report.html          # Policy check results
│   ├── policy-results.json                    # JSON export
│   └── license-changes-report.html            # Change detection report
│
├── alternatives/                              # Created during workflow
│   ├── alternatives-package1.html             # Alternative packages
│   └── alternatives-package2.html
│
├── uncertain-packages/                        # Created during workflow
│   ├── uncertain-packages.json                # Packages with missing licenses
│   ├── uncertain-package-ids.txt              # Simple ID list
│   └── report.md                              # Summary report
│
├── pypi-licenses/                             # Created during workflow
│   ├── pypi-licenses-full.json                # All PyPI results
│   ├── pypi-licenses-found.json               # Found licenses only
│   ├── pypi-licenses.csv                      # Spreadsheet format
│   └── curation-suggestions.yml               # ORT curations
│
├── scancode-results/                          # Created during workflow
│   ├── package1-1.0.json                      # Individual scan results
│   ├── package1-1.0.html
│   └── package1-1.0.yml
│
├── enhanced-spdx/                             # Created during workflow
│   ├── bom-enhanced.spdx.json                 # SPDX + ScanCode
│   ├── bom-enhanced-fixed.spdx.json           # Validated SPDX
│   └── merge-report.md                        # Merge statistics
│
├── public/                                    # GitHub Pages deployment
│   ├── index.html                             # Landing page
│   ├── policy-compliance-report.html
│   ├── license-changes-report.html
│   ├── alternatives/
│   ├── scancode-reports/
│   └── ... (all reports)
│
└── your-source-code/
    └── ...
```

---

## 🔄 Workflow Stages

### Stage 1: ORT Analysis (3-5 minutes)

**Purpose:** Analyze all dependencies and generate initial reports

**Steps:**
1. Run ORT Analyzer
   - Detects all project dependencies
   - Extracts declared licenses
   - Generates `analyzer-result.yml`

2. Run ORT Advisor
   - Cross-references against OSV vulnerability database
   - Generates `advise-result.yml`

3. Generate Initial Reports
   - WebApp (interactive HTML)
   - StaticHTML (simple HTML)
   - CycloneDX SBOM (JSON)
   - SPDX Document (YAML)

**Outputs:**
- `ort-results/analyzer/analyzer-result.yml` ← Used by all subsequent stages
- `ort-results/advisor/advise-result.yml`
- `ort-results/reporter/*.html`, `*.json`, `*.yml`

**Dependencies:** None

---

### Stage 2: Policy Compliance Check (30 seconds)

**Purpose:** Check all packages against company policy

**Steps:**
1. Load company policy (`company-policy.yml`)
2. For each package in `analyzer-result.yml`:
   - Extract declared license
   - Normalize SPDX identifier
   - Check against approved/conditional/forbidden lists
   - Calculate risk level
3. Generate compliance score (0-100%)
4. Export HTML report + JSON data

**Outputs:**
- `policy-reports/policy-compliance-report.html` (human-readable)
- `policy-reports/policy-results.json` (machine-readable)

**Exit Codes:**
- `0` - Success, no forbidden packages
- `1` - Failure, forbidden packages detected (fails build)

**Dependencies:**
- Requires: `ort-results/analyzer/analyzer-result.yml`
- Requires: `workflow_components/config/company-policy.yml`

---

### Stage 3: License Change Monitoring (30 seconds)

**Purpose:** Detect license changes over time

**Steps:**
1. **First run (init):**
   - Create `.ort/license-history.json`
   - Record all current licenses
   - Set baseline

2. **Subsequent runs (check):**
   - Load historical data
   - Compare current licenses vs. history
   - For each change:
     - Assess severity (CRITICAL/HIGH/MEDIUM/LOW)
     - Determine risk (e.g., MIT → GPL = CRITICAL)
     - Generate recommended actions
   - Update history database
   - Generate alert report

**Severity Assessment:**
- **CRITICAL:** Permissive → Copyleft (MIT → GPL)
- **HIGH:** License family change (Apache → BSD)
- **MEDIUM:** Version change within family (GPL-2.0 → GPL-3.0)
- **LOW:** Clarification only (MIT → MIT OR Apache-2.0)

**Outputs:**
- `.ort/license-history.json` (tracking database)
- `policy-reports/license-changes-report.html`
- `license-history/changes.json`

**Exit Codes:**
- `0` - Success, no critical changes
- `1` - Failure, critical changes detected (with `--fail-on-critical`)

**Dependencies:**
- Requires: `ort-results/analyzer/analyzer-result.yml`
- Optional: `workflow_components/config/company-policy.yml` (for policy-aware severity)

---

### Stage 4: Find Alternative Packages (1-2 minutes)

**Purpose:** Find replacement packages for forbidden licenses

**Steps:**
1. Load forbidden packages from `policy-results.json`
2. For each forbidden package (max 5):
   - Extract package name, type (PyPI/NPM), current license
   - Search package registry (PyPI API / NPM Registry)
   - Filter by approved licenses from policy
   - Rank alternatives by:
     - License compatibility (40%)
     - Popularity (25%)
     - Maintenance (20%)
     - Documentation (10%)
     - Security (5%)
   - Generate comparison report

**Ranking Factors:**
```python
score = (
    license_compatibility * 0.40 +  # Must be approved
    popularity_score * 0.25 +       # Monthly downloads
    maintenance_score * 0.20 +      # Last update recency
    documentation_score * 0.10 +    # Has docs, examples
    security_score * 0.05           # No CVEs, maintained
)
```

**Outputs:**
- `alternatives/alternatives-{package-name}.html` (one per forbidden package)

**Dependencies:**
- Requires: `policy-reports/policy-results.json`
- Requires: `workflow_components/config/company-policy.yml`
- Requires: Internet access (PyPI/NPM APIs)

---

### Stage 5: Extract Uncertain Packages (10 seconds)

**Purpose:** Identify packages with missing/uncertain licenses

**Steps:**
1. Load `analyzer-result.yml`
2. Filter packages where:
   - License = `NOASSERTION`
   - License = `UNKNOWN`
   - License = `NONE`
   - License is empty/null
3. Export multiple formats

**Outputs:**
- `uncertain-packages/uncertain-packages.json`
- `uncertain-packages/uncertain-package-ids.txt`
- `uncertain-packages/report.md`
- `uncertain-packages/extraction-stats.txt`

**Dependencies:**
- Requires: `ort-results/analyzer/analyzer-result.yml`

---

### Stage 6: Fetch PyPI Licenses (30 seconds)

**Purpose:** Fast license lookup from PyPI API

**Steps:**
1. Load uncertain packages
2. For each PyPI package:
   - Query PyPI API: `https://pypi.org/pypi/{name}/json`
   - Extract license from:
     - `info.license` field
     - `info.license_expression` field
     - `info.classifiers` (License :: ...)
   - Normalize to SPDX identifier
3. Generate curation suggestions
4. Export results

**Outputs:**
- `pypi-licenses/pypi-licenses-full.json` (all packages)
- `pypi-licenses/pypi-licenses-found.json` (found licenses only)
- `pypi-licenses/pypi-licenses.csv`
- `pypi-licenses/curation-suggestions.yml` (ORT format)

**Benefits:**
- Fast (no downloading/scanning needed)
- Reduces ScanCode workload by ~60-80%
- Free API (no quota limits)

**Dependencies:**
- Requires: `uncertain-packages/uncertain-packages.json`
- Requires: Internet access (PyPI API)

---

### Stage 7: ScanCode Deep Scan (5-15 minutes)

**Purpose:** Deep source code license detection

**Steps:**
1. Load uncertain packages
2. Load PyPI results to skip already-found licenses
3. For remaining packages (max 20):
   - Download source artifact
   - Extract to temporary directory
   - Run ScanCode:
     ```bash
     scancode -clpieu \
       --json package.json \
       --html package.html \
       --yaml package.yml \
       --timeout 120 \
       --max-depth 3 \
       ./package-directory
     ```
   - Extract license findings (confidence ≥80%)
4. Generate summary reports

**ScanCode Flags:**
- `-c` - Copyright detection
- `-l` - License detection
- `-p` - Package info
- `-i` - File info
- `-e` - Email detection
- `-u` - URL detection

**Outputs:**
- `scancode-results/{package}-{version}.json` (one per package)
- `scancode-results/{package}-{version}.html`
- `scancode-results/{package}-{version}.yml`

**Dependencies:**
- Requires: `uncertain-packages/scan-list.txt`
- Requires: `pypi-licenses/pypi-licenses-found.json` (to skip)
- Requires: Network access (to download packages)

---

### Stage 8: Merge ScanCode Results (30 seconds)

**Purpose:** Combine ScanCode findings into SPDX

**Steps:**
1. Load original SPDX (`bom.spdx.yml`)
2. Load all ScanCode JSON files
3. For each ScanCode result:
   - Match package name (fuzzy matching)
   - Extract high-confidence licenses (≥80% score)
   - Update SPDX package:
     - `licenseConcluded` - Detected license
     - `licenseComments` - Source: ScanCode
4. Validate and fix SPDX issues
5. Generate merge report

**Outputs:**
- `enhanced-spdx/bom-enhanced.spdx.json`
- `enhanced-spdx/bom-enhanced-fixed.spdx.json`
- `enhanced-spdx/merge-report.md`

**Dependencies:**
- Requires: `ort-results/reporter/bom.spdx.yml`
- Requires: `scancode-results/*.json`

---

### Stage 9: AI-Powered Curation (2-5 minutes, optional)

**Purpose:** AI analysis and recommendations

**5 AI Reports:**

#### 9a. Main ORT Curation Report
- Comprehensive project analysis
- License distribution
- Risk assessment
- Go/No-Go verdict

#### 9b. Conflict Analysis
- ORT vs ScanCode conflicts
- Evidence-based resolution
- Risk per package

#### 9c. Missing Licenses Analysis
- AI research for blank licenses
- Suggested licenses with confidence
- Verification steps

#### 9d. Multi-Layer Comparison
- Compare all sources (ORT/PyPI/ScanCode/SPDX)
- No AI, just data aggregation

#### 9e. AI Multi-Layer Resolution
- AI-powered conflict resolution
- Combines all data sources
- Actionable recommendations

**Dependencies:**
- Requires: `ort-results/analyzer/analyzer-result.yml`
- Optional: `uncertain-packages/uncertain-packages.json`
- Optional: `enhanced-spdx/bom-enhanced-fixed.spdx.json`
- Optional: `pypi-licenses/pypi-licenses-full.json`
- Optional: `scancode-results/`
- Requires: Azure OpenAI credentials

**Cost:** ~$0.20-$0.33 per run

---

### Stage 10-11: GitHub Pages Deployment (1-2 minutes)

**Purpose:** Deploy all reports to GitHub Pages

**Steps:**
1. Create `public/` directory
2. Copy all reports:
   - ORT reports
   - Policy reports
   - License change alerts
   - Alternative packages
   - AI curation reports
   - ScanCode reports
   - PyPI results
   - Enhanced SPDX
3. Generate landing page (index.html)
4. Upload to GitHub Pages
5. Deploy

**Outputs:**
- `public/` directory with all reports
- Deployed to: `https://<org>.github.io/<repo>/`

**Dependencies:**
- Requires: All previous stages completed

---

### Stage 12: Artifact Upload (1 minute)

**Purpose:** Preserve all results

**Artifacts:**
1. `ort-results-{branch}-{run_number}` (30 days)
2. `scancode-results-{branch}-{run_number}` (30 days)
3. `policy-reports-{branch}-{run_number}` (30 days)
4. `enhanced-reports-{branch}-{run_number}` (30 days)

**Dependencies:** None (always runs)

---

### Stage 13: Summary & PR Comment (10 seconds)

**Purpose:** Notify stakeholders

**Outputs:**
- GitHub Step Summary (workflow page)
- PR comment (if pull request)

**Dependencies:** None (always runs)

---

## 📊 Data Flow Diagram

```
┌─────────────┐
│ Source Code │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────┐
│ STAGE 1: ORT Analysis                    │
│ - ORT Analyzer                           │
│ - ORT Advisor (OSV)                      │
│ - ORT Reporter (SPDX, CycloneDX, HTML)   │
└──────┬───────────────────────────────────┘
       │
       ├─────────────────────────────────────┐
       │                                     │
       ▼                                     ▼
┌──────────────────┐              ┌──────────────────┐
│ STAGE 2: Policy  │              │ STAGE 3: Change  │
│ Compliance Check │              │ Monitoring       │
│                  │              │                  │
│ Output:          │              │ Input:           │
│ - Approved       │              │ - Current state  │
│ - Conditional    │              │ - History DB     │
│ - Forbidden ─────┼──┐           │                  │
│ - Unknown        │  │           │ Output:          │
└──────────────────┘  │           │ - Changes        │
                      │           │ - Severity       │
                      │           │ - Actions        │
                      │           └──────────────────┘
                      │
                      ▼
            ┌───────────────────┐
            │ STAGE 4: Find     │
            │ Alternatives      │
            │                   │
            │ For each          │
            │ forbidden pkg:    │
            │ - Search PyPI/NPM │
            │ - Rank by score   │
            │ - Generate report │
            └───────────────────┘

┌──────────────────────────────────────────┐
│ STAGE 5: Extract Uncertain Packages      │
│ - NOASSERTION, UNKNOWN, blank licenses   │
└──────┬───────────────────────────────────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ STAGE 6:     │  │ STAGE 7:     │
│ PyPI API     │  │ ScanCode     │
│ Fast lookup  │  │ Deep scan    │
│              │  │              │
│ Reduces      │  │ Remaining    │
│ ScanCode     │  │ packages     │
│ workload     │  │ only         │
└──────┬───────┘  └──────┬───────┘
       │                 │
       └────────┬────────┘
                │
                ▼
       ┌────────────────┐
       │ STAGE 8: Merge │
       │ Into SPDX      │
       │                │
       │ - Combine all  │
       │ - Validate     │
       │ - Fix issues   │
       └────────┬───────┘
                │
                ▼
       ┌────────────────────┐
       │ STAGE 9: AI        │
       │ Analysis (optional)│
       │                    │
       │ - Main curation    │
       │ - Conflicts        │
       │ - Missing licenses │
       │ - Multi-layer      │
       └────────┬───────────┘
                │
                ▼
       ┌────────────────────┐
       │ STAGE 10-11:       │
       │ GitHub Pages       │
       │                    │
       │ - Collect reports  │
       │ - Landing page     │
       │ - Deploy           │
       └────────────────────┘
```

---

## 🔌 Integration Points

### Input Files Required
1. **Source code** - Your project to analyze
2. **company-policy.yml** - Your license policy
3. **(Optional) .ort/license-history.json** - For change tracking

### External Services
1. **PyPI API** - `https://pypi.org/pypi/{package}/json`
2. **NPM Registry** - `https://registry.npmjs.org/{package}`
3. **GitHub API** - For PR comments
4. **Azure OpenAI** - For AI features (optional)
5. **OSV Database** - Via ORT Advisor
6. **GitHub Pages** - For report deployment

### Environment Variables
```bash
# Required for AI features only
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_MODEL=your-deployment-name

# Auto-provided by GitHub Actions
GITHUB_WORKSPACE=/github/workspace
GITHUB_REPOSITORY=owner/repo
GITHUB_REF=refs/heads/main
GITHUB_RUN_ID=1234567890
GITHUB_STEP_SUMMARY=/path/to/summary
```

---

## 📄 File Outputs Summary

### Critical Files (Version Controlled)
```bash
.ort/license-history.json        # License change tracking DB (commit to git!)
workflow_components/             # All workflow scripts and configs (commit to git!)
.github/workflows/*.yml          # Workflow definition (commit to git!)
```

### Generated Files (Not Version Controlled)
```bash
ort-results/                     # ORT analysis outputs
policy-reports/                  # Policy compliance results
license-history/                 # Change detection results
alternatives/                    # Alternative package reports
uncertain-packages/              # Missing license lists
pypi-licenses/                   # PyPI API results
scancode-results/                # ScanCode scan results
enhanced-spdx/                   # Enhanced SPDX documents
public/                          # GitHub Pages deployment
*.log                            # Execution logs
```

### Artifact Retention
- All results uploaded as GitHub Actions artifacts
- Retention: 30 days
- Download anytime via Actions → Artifacts

---

## ⏱️ Timing Estimates

| Stage | Duration | Can Skip? |
|-------|----------|-----------|
| 1. ORT Analysis | 3-5 min | No |
| 2. Policy Check | 30 sec | No (critical) |
| 3. Change Monitor | 30 sec | Yes (first run) |
| 4. Find Alternatives | 1-2 min | Yes (if no forbidden) |
| 5. Extract Uncertain | 10 sec | No |
| 6. PyPI Fetch | 30 sec | Yes |
| 7. ScanCode Scan | 5-15 min | Yes |
| 8. Merge SPDX | 30 sec | Yes |
| 9. AI Analysis | 2-5 min | Yes (requires Azure) |
| 10-11. Deploy | 1-2 min | Yes |
| 12. Artifacts | 1 min | No |
| 13. Summary | 10 sec | No |
| **Total** | **15-35 min** | |

**Typical run time:** ~20 minutes

---

## 🎯 Success Criteria

**Workflow succeeds when:**
- ✅ No forbidden packages detected
- ✅ No critical license changes detected
- ✅ Compliance score >95% (configurable)
- ✅ All conditional licenses have approval

**Workflow fails when:**
- ❌ Forbidden packages detected
- ❌ Critical license changes detected (with `--fail-on-critical`)
- ❌ Compliance score <threshold (configurable)

**Failure is good!** It prevents non-compliant code from being deployed.

---

**Made with ❤️ for software compliance teams**

*Last Updated: 2025-01-19*
