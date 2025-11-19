# Workflow Diagrams - Complete License Curation System

> Visual representation of all workflows in the Enhanced ORT License Curation System with Advanced Policy Management

---

## Table of Contents

1. [Overall System Architecture](#overall-system-architecture)
2. [Enhanced ORT Workflow (GitHub Actions)](#enhanced-ort-workflow-github-actions)
3. [Advanced License Curation Workflow](#advanced-license-curation-workflow)
4. [Policy Compliance Decision Tree](#policy-compliance-decision-tree)
5. [License Change Monitoring Flow](#license-change-monitoring-flow)
6. [Alternative Package Finding Process](#alternative-package-finding-process)
7. [Complete Integration Architecture](#complete-integration-architecture)
8. [Daily Operations Flow](#daily-operations-flow)

---

## Overall System Architecture

```mermaid
graph TB
    A[Source Code Repository] --> B[GitHub Actions Trigger]
    B --> C{Trigger Type?}
    C -->|Push to main| D[Full Workflow]
    C -->|Pull Request| E[Analysis Only]
    C -->|Manual Dispatch| D
    C -->|Scheduled| D

    D --> F[Stage 1: ORT Analysis]
    F --> G[Stage 2: Extract Uncertain Packages]
    G --> H[Stage 2.5: PyPI API Fetch]
    H --> I[Stage 3: ScanCode Deep Scan]
    I --> J[Stage 4: Merge & Validate]
    J --> K[Stage 5: AI Curation]
    K --> L[Stage 6: Prepare Deployment]
    L --> M[Stage 7: Deploy to GitHub Pages]

    E --> F
    F --> G
    G --> N[Generate Reports Only]
    N --> O[Upload Artifacts]

    M --> P[GitHub Pages Site]
    P --> Q[Stakeholders View Reports]

    O --> R[Artifact Storage 30 days]

    style A fill:#e1f5ff
    style P fill:#c8e6c9
    style Q fill:#fff9c4
    style D fill:#ffccbc
    style K fill:#f8bbd0
```

---

## Enhanced ORT Workflow (GitHub Actions)

### Complete Workflow Stages

```mermaid
flowchart TD
    Start([Workflow Triggered]) --> Setup[Setup Environment]
    Setup --> InstallORT[Install ORT 70.0.1]
    InstallORT --> InstallPython[Install Python Dependencies]

    InstallPython --> Stage1{Stage 1: ORT Analysis}

    Stage1 --> Analyzer[ORT Analyzer<br/>Dependency Analysis]
    Analyzer --> Advisor[ORT Advisor<br/>OSV Vulnerability Scan]
    Advisor --> Reporter[ORT Reporter<br/>Generate SPDX, CycloneDX, WebApp, HTML]

    Reporter --> Stage2{Stage 2: Extract Uncertain}
    Stage2 --> Extract[Extract Uncertain Packages<br/>Python Script]
    Extract --> CheckUncertain{Uncertain<br/>Packages<br/>Found?}

    CheckUncertain -->|Yes| Stage25[Stage 2.5: PyPI Fetch]
    CheckUncertain -->|No| SkipScan[Skip ScanCode]

    Stage25 --> FetchPyPI[Fetch PyPI Licenses<br/>API Calls - Fast]
    FetchPyPI --> GenPyPIReport[Generate PyPI HTML Report]
    GenPyPIReport --> Stage3{Stage 3: ScanCode}

    Stage3 --> DownloadPkgs[Download Package Sources<br/>First 20 packages]
    DownloadPkgs --> ScanCode[ScanCode Deep Scan<br/>-clpieu flags<br/>HTML/JSON/YAML per package]
    ScanCode --> ConsolidateScan[Generate ScanCode<br/>Consolidated Reports]

    ConsolidateScan --> Stage4{Stage 4: Merge & Validate}
    SkipScan --> Stage4

    Stage4 --> MergeSPDX[Merge ScanCode to SPDX<br/>Python Script]
    MergeSPDX --> ValidateSPDX[Validate & Fix SPDX<br/>Python Script]
    ValidateSPDX --> Stage5{Stage 5: AI Curation}

    Stage5 --> CheckAI{Azure OpenAI<br/>Configured?}

    CheckAI -->|Yes| AI5a[5a: Main ORT Curation<br/>gpt-4.1-mini]
    CheckAI -->|No| SkipAI[Skip AI Reports]

    AI5a --> CheckConflicts{Uncertain<br/>Packages?}
    CheckConflicts -->|Yes| AI5b[5b: Conflict Analysis<br/>gpt-4]
    CheckConflicts -->|No| AI5c

    AI5b --> CheckMissing{Missing<br/>Licenses?}
    CheckMissing -->|Yes| AI5c[5c: Missing Licenses<br/>gpt-4o-mini<br/>Max 15 packages]
    CheckMissing -->|No| Stage5d

    AI5c --> Stage5d{Stage 5d:<br/>License Comparison}
    SkipAI --> Stage5d

    Stage5d --> GenComparison[Generate Multi-Layer<br/>License Comparison<br/>No AI - Pure Comparison]

    GenComparison --> Stage5e{Stage 5e:<br/>AI Resolution}
    Stage5e --> CheckAI2{Azure OpenAI<br/>Configured?}

    CheckAI2 -->|Yes| GenResolution[Generate AI Multi-Layer<br/>Resolution Report<br/>gpt-4.1-mini<br/>15 conflicts + 10 missing]
    CheckAI2 -->|No| SkipResolution[Skip AI Resolution]

    GenResolution --> Stage6{Stage 6:<br/>Prepare Deployment}
    SkipResolution --> Stage6

    Stage6 --> CopyReports[Copy All Reports to public/]
    CopyReports --> GenLanding[Generate Landing Page<br/>Auto-detect all reports]

    GenLanding --> CheckBranch{Branch is<br/>main or master?}

    CheckBranch -->|Yes| Stage7{Stage 7:<br/>Deploy Pages}
    CheckBranch -->|No| SkipDeploy[Skip Deployment]

    Stage7 --> SetupPages[Setup GitHub Pages]
    SetupPages --> UploadPages[Upload Pages Artifact]
    UploadPages --> DeployPages[Deploy to GitHub Pages]

    DeployPages --> Stage8{Stage 8:<br/>Upload Artifacts}
    SkipDeploy --> Stage8

    Stage8 --> UploadORT[Upload ORT Results<br/>30 days retention]
    UploadORT --> UploadScan[Upload ScanCode Results<br/>30 days retention]
    UploadScan --> UploadEnhanced[Upload Enhanced Reports<br/>30 days retention]

    UploadEnhanced --> End([Workflow Complete])

    style Start fill:#4caf50,color:#fff
    style End fill:#4caf50,color:#fff
    style Stage1 fill:#2196f3,color:#fff
    style Stage2 fill:#2196f3,color:#fff
    style Stage25 fill:#ff9800,color:#fff
    style Stage3 fill:#2196f3,color:#fff
    style Stage4 fill:#2196f3,color:#fff
    style Stage5 fill:#9c27b0,color:#fff
    style Stage5d fill:#ff9800,color:#fff
    style Stage5e fill:#9c27b0,color:#fff
    style Stage6 fill:#00bcd4,color:#fff
    style Stage7 fill:#00bcd4,color:#fff
    style Stage8 fill:#607d8b,color:#fff
```

---

## Advanced License Curation Workflow

### Policy-Based Compliance System

```mermaid
flowchart TB
    Start([ORT Results Available]) --> LoadPolicy[Load Company Policy<br/>company-policy.yml]
    LoadPolicy --> ParseORT[Parse ORT Results<br/>Extract Package Licenses]

    ParseORT --> Loop{For Each<br/>Package}

    Loop --> GetLicense[Get Package License<br/>declared/concluded]

    GetLicense --> NormalizeLic[Normalize License<br/>BSD License → BSD-3-Clause]

    NormalizeLic --> CheckPolicy{Check Against<br/>Company Policy}

    CheckPolicy -->|Found in Approved| Approved[Status: APPROVED<br/>Auto-approve: True<br/>Risk: LOW]
    CheckPolicy -->|Found in Conditional| Conditional[Status: CONDITIONAL<br/>Approval Required<br/>Risk: MEDIUM]
    CheckPolicy -->|Found in Forbidden| Forbidden[Status: FORBIDDEN<br/>Alternative Needed<br/>Risk: CRITICAL]
    CheckPolicy -->|Not Found| Unknown[Status: UNKNOWN<br/>Research Required<br/>Risk: HIGH]

    Approved --> CheckDual{Dual License?<br/>MIT OR Apache}
    Conditional --> CheckApprovers[Identify Approvers<br/>legal@company.com]
    Forbidden --> FindAlt[Trigger Alternative<br/>Package Finder]
    Unknown --> ResearchPath[Research Path<br/>PyPI → ScanCode → Manual]

    CheckDual -->|Yes| ChooseBest[Choose Most Permissive<br/>Per Policy Strategy]
    CheckDual -->|No| StoreResult

    ChooseBest --> StoreResult[Store Result<br/>PolicyCheckResult]
    CheckApprovers --> StoreResult
    FindAlt --> StoreResult
    ResearchPath --> StoreResult

    StoreResult --> MorePackages{More<br/>Packages?}
    MorePackages -->|Yes| Loop
    MorePackages -->|No| CalcScore[Calculate Compliance Score<br/>Approved / Total × 100]

    CalcScore --> GenReport[Generate HTML Report<br/>Color-coded Status]
    GenReport --> ExportJSON[Export JSON<br/>For Automation]

    ExportJSON --> CheckCritical{Forbidden or<br/>Critical Risk?}
    CheckCritical -->|Yes| FailBuild[Exit Code 1<br/>Fail CI/CD Build]
    CheckCritical -->|No| PassBuild[Exit Code 0<br/>Pass Build]

    FailBuild --> End([Complete])
    PassBuild --> End

    style Start fill:#4caf50,color:#fff
    style End fill:#4caf50,color:#fff
    style Approved fill:#c8e6c9
    style Conditional fill:#fff9c4
    style Forbidden fill:#ffcdd2
    style Unknown fill:#e0e0e0
    style FailBuild fill:#f44336,color:#fff
    style PassBuild fill:#4caf50,color:#fff
```

---

## Policy Compliance Decision Tree

### Master Decision Logic

```mermaid
flowchart TD
    Start([Package License<br/>Detection]) --> Normalize[Normalize License String]

    Normalize --> CheckType{License<br/>Expression<br/>Type?}

    CheckType -->|Single| Single[Single License<br/>e.g., MIT]
    CheckType -->|OR| DualLic[Dual License<br/>e.g., MIT OR Apache-2.0]
    CheckType -->|AND| MultiLic[Multi License<br/>e.g., MIT AND BSD-3-Clause]

    Single --> LookupSingle[Lookup in Policy Database]
    DualLic --> Strategy{Policy<br/>Strategy?}
    MultiLic --> CheckCompat[Check Compatibility Matrix]

    Strategy -->|choose_most_permissive| ChoosePerm[Choose Most Permissive<br/>Prefer Approved]
    Strategy -->|manual_review| ManualRev[Flag for Manual Review]

    ChoosePerm --> LookupSingle
    ManualRev --> Conditional
    CheckCompat --> Compatible{All<br/>Compatible?}

    Compatible -->|Yes| AllApproved{All<br/>Approved?}
    Compatible -->|No| Incompatible[Status: INCOMPATIBLE<br/>Risk: CRITICAL]

    AllApproved -->|Yes| Approved
    AllApproved -->|No| AnyForbidden{Any<br/>Forbidden?}

    AnyForbidden -->|Yes| Forbidden
    AnyForbidden -->|No| Conditional

    LookupSingle --> Found{Found in<br/>Policy?}

    Found -->|Approved List| Approved[✅ APPROVED<br/>Green Status<br/>Auto-approve]
    Found -->|Conditional List| Conditional[⚠️ CONDITIONAL<br/>Yellow Status<br/>Needs Approval]
    Found -->|Forbidden List| Forbidden[❌ FORBIDDEN<br/>Red Status<br/>Find Alternative]
    Found -->|Not Found| Unknown[❓ UNKNOWN<br/>Gray Status<br/>Research]

    Approved --> Actions1[Actions:<br/>- Generate Curation<br/>- Proceed with Build]
    Conditional --> Actions2[Actions:<br/>- Request Approval<br/>- Document Use Case<br/>- Wait for Decision]
    Forbidden --> Actions3[Actions:<br/>- Find Alternatives<br/>- Reject Package<br/>- Fail Build]
    Unknown --> Actions4[Actions:<br/>- Research License<br/>- Check PyPI/ScanCode<br/>- Manual Verification]
    Incompatible --> Actions5[Actions:<br/>- Review Combination<br/>- Legal Consultation<br/>- Fail Build]

    Actions1 --> End([Decision Complete])
    Actions2 --> End
    Actions3 --> End
    Actions4 --> End
    Actions5 --> End

    style Start fill:#2196f3,color:#fff
    style End fill:#4caf50,color:#fff
    style Approved fill:#c8e6c9
    style Conditional fill:#fff9c4
    style Forbidden fill:#ffcdd2
    style Unknown fill:#e0e0e0
    style Incompatible fill:#ffcdd2
```

---

## License Change Monitoring Flow

### Historical Tracking and Alert System

```mermaid
flowchart TB
    Start([ORT Scan Complete]) --> CheckHistory{License History<br/>Database Exists?}

    CheckHistory -->|No| InitMode[INITIALIZATION MODE]
    CheckHistory -->|Yes| CheckMode[CHANGE DETECTION MODE]

    InitMode --> CreateDB[Create Empty Database<br/>.ort/license-history.json]
    CreateDB --> ParsePkgs1[Parse All Packages<br/>from ORT Results]
    ParsePkgs1 --> SaveBaseline[Save Baseline<br/>First Entry per Package]
    SaveBaseline --> InitComplete[Initialization Complete<br/>Total Scans: 1]

    CheckMode --> ParsePkgs2[Parse Current Packages<br/>from ORT Results]
    ParsePkgs2 --> Loop{For Each<br/>Package}

    Loop --> CheckExists{Package in<br/>History?}

    CheckExists -->|No| NewPkg[NEW PACKAGE<br/>Add to History]
    CheckExists -->|Yes| CompareLic[Compare Current License<br/>vs Previous License]

    CompareLic --> Changed{License<br/>Changed?}

    Changed -->|No| UpdateVerified[Update Last Verified Date]
    Changed -->|Yes| DetectChange[CHANGE DETECTED!]

    DetectChange --> AssessSeverity[Assess Change Severity<br/>Using Policy Rules]

    AssessSeverity --> SevType{Change<br/>Type?}

    SevType -->|Permissive → Copyleft| Critical[⛔ CRITICAL<br/>MIT → GPL-3.0<br/>Requires Immediate Action]
    SevType -->|Copyleft → Permissive| High[⚠️ HIGH<br/>GPL-3.0 → MIT<br/>Unusual - Verify]
    SevType -->|Version Change Same Family| Medium[📋 MEDIUM<br/>GPL-2.0 → GPL-3.0<br/>Review New Terms]
    SevType -->|Permissive → Permissive| Low[ℹ️ LOW<br/>MIT → Apache-2.0<br/>Document Change]

    Critical --> Actions1[Actions:<br/>1. Stop using immediately<br/>2. Legal review<br/>3. Revert to safe version<br/>4. Find alternative]
    High --> Actions2[Actions:<br/>1. Verify legitimacy<br/>2. Check maintainer comms<br/>3. Review new terms<br/>4. Consider alternatives]
    Medium --> Actions3[Actions:<br/>1. Review new license<br/>2. Check compatibility<br/>3. Update docs]
    Low --> Actions4[Actions:<br/>1. Note in documentation<br/>2. Verify compliance]

    Actions1 --> LogChange[Log Change to History<br/>change_detected: true]
    Actions2 --> LogChange
    Actions3 --> LogChange
    Actions4 --> LogChange

    NewPkg --> LogChange
    UpdateVerified --> LogChange

    LogChange --> MorePkgs{More<br/>Packages?}
    MorePkgs -->|Yes| Loop
    MorePkgs -->|No| IncrementScan[Increment Total Scans]

    IncrementScan --> SaveDB[Save Updated Database]
    SaveDB --> GenReport[Generate Change Alert Report<br/>HTML with Recommended Actions]

    GenReport --> CheckCritical{Critical<br/>Changes?}
    CheckCritical -->|Yes| FailBuild[Fail Build<br/>Exit Code 1<br/>Block Deployment]
    CheckCritical -->|No| PassBuild[Pass Build<br/>Exit Code 0]

    FailBuild --> End([Monitoring Complete])
    PassBuild --> End
    InitComplete --> End

    style Start fill:#2196f3,color:#fff
    style End fill:#4caf50,color:#fff
    style Critical fill:#f44336,color:#fff
    style High fill:#ff9800,color:#fff
    style Medium fill:#ffc107
    style Low fill:#4caf50,color:#fff
    style FailBuild fill:#f44336,color:#fff
    style PassBuild fill:#4caf50,color:#fff
```

---

## Alternative Package Finding Process

### Smart Replacement Recommendations

```mermaid
flowchart TB
    Start([Forbidden License<br/>Detected]) --> GetInfo[Get Package Info<br/>Name, Type, License]

    GetInfo --> FetchMeta[Fetch Package Metadata<br/>Description, Keywords, Category]

    FetchMeta --> ExtractKeywords[Extract Keywords<br/>From Description & Classifiers]

    ExtractKeywords --> BuildSearch[Build Search Terms<br/>Keywords + Category + Name Parts]

    BuildSearch --> SearchReg{Package<br/>Type?}

    SearchReg -->|PyPI| SearchPyPI[Search PyPI API<br/>Multiple Search Terms]
    SearchReg -->|NPM| SearchNPM[Search NPM Registry<br/>Multiple Search Terms]
    SearchReg -->|Maven| SearchMaven[Search Maven Central<br/>Multiple Search Terms]

    SearchPyPI --> GetResults[Get Search Results<br/>Max 20 per search term]
    SearchNPM --> GetResults
    SearchMaven --> GetResults

    GetResults --> FilterLoop{For Each<br/>Result}

    FilterLoop --> SkipOriginal{Same as<br/>Original?}
    SkipOriginal -->|Yes| NextResult
    SkipOriginal -->|No| FetchDetail[Fetch Detailed Package Info<br/>License, Stats, Repo]

    FetchDetail --> ExtractLic[Extract License<br/>Normalize to SPDX]

    ExtractLic --> CheckApproved{License in<br/>Approved List?}
    CheckApproved -->|No| NextResult
    CheckApproved -->|Yes| GetStats[Get Package Statistics<br/>Downloads, Stars, Updates]

    GetStats --> CalcScores[Calculate Scores]

    CalcScores --> LicScore[License Compatibility Score<br/>40% weight<br/>Permissive = 1.0<br/>Weak Copyleft = 0.8]
    LicScore --> PopScore[Popularity Score<br/>25% weight<br/>log10 scale]
    PopScore --> MaintScore[Maintenance Score<br/>20% weight<br/>Based on last update]

    MaintScore --> TotalScore[Total Score<br/>Weighted Sum<br/>0.0 - 1.0]

    TotalScore --> AddCandidate[Add to Candidates List]

    AddCandidate --> NextResult{More<br/>Results?}
    NextResult -->|Yes| FilterLoop
    NextResult -->|No| RankResults[Rank by Total Score<br/>Descending]

    RankResults --> TopN[Select Top 5 Alternatives]

    TopN --> GenReport[Generate HTML Report<br/>Side-by-Side Comparison]

    GenReport --> ReportContents[Report Contents:<br/>- Scores breakdown<br/>- License comparison<br/>- Popularity metrics<br/>- Maintenance status<br/>- Verification links]

    ReportContents --> CheckFound{Alternatives<br/>Found?}
    CheckFound -->|Yes| Success[Return Alternatives<br/>Exit Code 0]
    CheckFound -->|No| NoAlt[No Alternatives Found<br/>Manual Search Required<br/>Exit Code 0]

    Success --> End([Process Complete])
    NoAlt --> End

    style Start fill:#f44336,color:#fff
    style End fill:#4caf50,color:#fff
    style Success fill:#c8e6c9
    style NoAlt fill:#fff9c4
    style CheckApproved fill:#2196f3,color:#fff
```

---

## Complete Integration Architecture

### How All Components Work Together

```mermaid
graph TB
    subgraph "Source Repository"
        A[Source Code] --> B[Dependencies<br/>package.json, requirements.txt]
    end

    subgraph "CI/CD Pipeline - GitHub Actions"
        B --> C[Trigger Workflow<br/>Push/PR/Schedule]
        C --> D[Enhanced ORT Workflow<br/>Stages 1-8]
    end

    subgraph "Stage 1-2: Basic Analysis"
        D --> E[ORT Analyzer<br/>Dependency Detection]
        E --> F[Extract Uncertain Packages<br/>NOASSERTION/UNKNOWN]
    end

    subgraph "Stage 2.5-3: Deep Analysis"
        F --> G[PyPI API Fetch<br/>Fast License Retrieval]
        G --> H[ScanCode Deep Scan<br/>File-level Detection]
    end

    subgraph "Stage 4: Data Consolidation"
        H --> I[Merge Results<br/>ORT + PyPI + ScanCode]
        I --> J[Validate & Fix SPDX<br/>ISO/IEC 5962:2021]
    end

    subgraph "Stage 5: AI Analysis (Optional)"
        J --> K[Main ORT Curation<br/>gpt-4.1-mini]
        K --> L[Conflict Analysis<br/>gpt-4]
        L --> M[Missing Licenses<br/>gpt-4o-mini]
        M --> N[Multi-Layer Comparison<br/>No AI]
        N --> O[AI Resolution<br/>gpt-4.1-mini]
    end

    subgraph "Advanced Policy Management (NEW)"
        O --> P[Policy Checker<br/>policy_checker.py]
        P --> Q{Policy<br/>Decision}
        Q -->|Approved| R[✅ Generate Curation]
        Q -->|Conditional| S[⚠️ Request Approval]
        Q -->|Forbidden| T[❌ Find Alternatives]
        Q -->|Unknown| U[❓ Research Path]
    end

    subgraph "Alternative Finding (NEW)"
        T --> V[Alternative Package Finder<br/>alternative_package_finder.py]
        V --> W[Search Registries<br/>PyPI, NPM, Maven]
        W --> X[Rank by Score<br/>License, Popularity, Maintenance]
        X --> Y[Generate Comparison Report]
    end

    subgraph "License Change Monitoring (NEW)"
        P --> Z[License Change Monitor<br/>license_change_monitor.py]
        Z --> AA[Check History Database<br/>.ort/license-history.json]
        AA --> AB{Changes<br/>Detected?}
        AB -->|Yes| AC[Assess Severity<br/>CRITICAL/HIGH/MEDIUM/LOW]
        AB -->|No| AD[Update Last Verified]
        AC --> AE[Generate Alert Report<br/>Recommended Actions]
    end

    subgraph "Stage 6-7: Deployment"
        R --> AF[Prepare Reports<br/>Copy to public/]
        S --> AF
        Y --> AF
        AE --> AF
        AD --> AF
        U --> AF

        AF --> AG[Generate Landing Page<br/>Auto-detect All Reports]
        AG --> AH{Branch?}
        AH -->|main/master| AI[Deploy to GitHub Pages]
        AH -->|other| AJ[Skip Deployment]
    end

    subgraph "Stage 8: Artifact Storage"
        AI --> AK[Upload Artifacts<br/>30 days retention]
        AJ --> AK
        AK --> AL[ORT Results]
        AK --> AM[ScanCode Results]
        AK --> AN[Policy Reports]
        AK --> AO[Change Alerts]
        AK --> AP[Alternative Reports]
    end

    subgraph "Outputs & Access"
        AI --> AQ[GitHub Pages Site<br/>https://user.github.io/repo]
        AQ --> AR[Stakeholders View Reports:<br/>13+ Report Types]

        AL --> AS[Download for Offline Analysis]
        AM --> AS
        AN --> AS
        AO --> AS
        AP --> AS
    end

    subgraph "Manual Actions"
        S --> AT[Compliance Team<br/>Approval Workflow]
        U --> AU[Developer<br/>Manual Research]
        Y --> AV[Developer<br/>Test Alternative]

        AT --> AW[Update Curations<br/>.ort/curations.yml]
        AU --> AW
        AV --> AW
    end

    AW --> AX[Re-run Workflow<br/>Verify Fix]
    AX --> C

    style P fill:#ff9800,color:#fff
    style V fill:#ff9800,color:#fff
    style Z fill:#ff9800,color:#fff
    style AQ fill:#4caf50,color:#fff
    style R fill:#c8e6c9
    style S fill:#fff9c4
    style T fill:#ffcdd2
    style U fill:#e0e0e0
```

---

## Daily Operations Flow

### Typical Day-to-Day Usage

```mermaid
flowchart LR
    subgraph "Morning - Automated"
        A([2 AM UTC<br/>Scheduled Trigger]) --> B[Run Complete Workflow<br/>All Repositories]
        B --> C[Generate Reports<br/>Policy + Changes + Alternatives]
        C --> D{Issues<br/>Detected?}
        D -->|Yes| E[Send Email/Slack Alert<br/>Compliance Team]
        D -->|No| F[Update Dashboard<br/>All Green]
    end

    subgraph "Developer - Pull Request"
        G([Developer Creates PR]) --> H[PR Triggers Workflow<br/>Analysis Only]
        H --> I[Check Policy Compliance]
        I --> J{Forbidden or<br/>Critical?}
        J -->|Yes| K[❌ Fail PR Check<br/>Block Merge]
        J -->|No| L[✅ Pass PR Check<br/>Add Comment with Status]
        K --> M[Developer Reviews<br/>Policy Report]
        M --> N{Can Fix?}
        N -->|Yes| O[Replace Package<br/>Update PR]
        N -->|No| P[Request Exception<br/>Compliance Team]
    end

    subgraph "Compliance Team - Review"
        E --> Q[Open Alert Report]
        P --> Q
        Q --> R[Review Changes/Violations]
        R --> S{Decision}
        S -->|Approve| T[Add to Curations<br/>.ort/curations.yml]
        S -->|Reject| U[Request Developer<br/>Find Alternative]
        S -->|Escalate| V[Legal Team Review]
    end

    subgraph "Weekly - Audit"
        W([Friday End of Week]) --> X[Generate Compliance Summary<br/>Past 7 Days]
        X --> Y[Review Metrics:<br/>- Compliance Score Trend<br/>- License Changes<br/>- Approvals Pending]
        Y --> Z[Update Company Policy<br/>if Needed]
    end

    O --> AA[Re-run PR Check<br/>Verify Fix]
    T --> AA
    U --> M
    AA --> I

    F --> AB([Reports Available<br/>GitHub Pages])
    L --> AB
    Z --> AB

    style A fill:#2196f3,color:#fff
    style K fill:#f44336,color:#fff
    style L fill:#4caf50,color:#fff
    style T fill:#4caf50,color:#fff
    style AB fill:#4caf50,color:#fff
```

---

## Component Interaction Matrix

### How Each Component Communicates

| Component | Inputs | Outputs | Triggers |
|-----------|--------|---------|----------|
| **ORT Analyzer** | Source code, Dependencies | `analyzer-result.yml` | Manual, CI/CD |
| **Policy Checker** | ORT results, Policy YAML | Compliance report (HTML/JSON) | After ORT |
| **Alternative Finder** | Forbidden package info | Alternatives report (HTML) | When forbidden detected |
| **Change Monitor** | ORT results, History DB | Change alert report (HTML) | After ORT |
| **PyPI Fetcher** | Uncertain packages | PyPI licenses JSON | After extraction |
| **ScanCode** | Package sources | License detections (JSON) | After PyPI |
| **AI Curation** | All above results | Curation recommendations | After merge |
| **Landing Page** | All reports | Unified HTML index | Before deployment |

---

## Legend

### Status Colors

- 🟢 **Green** - Approved/Success/Pass
- 🟡 **Yellow** - Conditional/Warning/Needs Review
- 🔴 **Red** - Forbidden/Error/Fail
- ⚪ **Gray** - Unknown/Pending/Research Needed
- 🔵 **Blue** - Processing/In Progress
- 🟣 **Purple** - AI/ML Analysis
- 🟠 **Orange** - New Feature/Enhancement

### Severity Levels

- ⛔ **CRITICAL** - Immediate action required (permissive → copyleft)
- ⚠️ **HIGH** - Urgent review needed (unusual changes)
- 📋 **MEDIUM** - Review recommended (license family change)
- ℹ️ **LOW** - Awareness only (minor changes)

---

## Quick Reference

### Workflow Files Locations

```
Repository Root/
├── .github/workflows/
│   └── license-compliance.yml          # GitHub Actions workflow
│
├── Advanced_License_Curation_Workflow/
│   ├── config/
│   │   └── company-policy.yml         # Policy database
│   ├── scripts/
│   │   ├── policy_checker.py          # Policy compliance
│   │   ├── alternative_package_finder.py  # Find replacements
│   │   └── license_change_monitor.py  # Track changes
│   └── .ort/
│       └── license-history.json       # Historical tracking
│
└── ort-results/
    ├── analyzer/analyzer-result.yml   # ORT output
    └── reporter/bom.spdx.yml          # SPDX SBOM
```

---

**For detailed implementation guides, see:**
- [README.md](README.md) - Complete documentation
- [SETUP_SUMMARY.md](SETUP_SUMMARY.md) - Quick start guide
- [docs/QUICK_START.md](docs/QUICK_START.md) - 15-minute tutorial

*Generated: 2025-01-16*
