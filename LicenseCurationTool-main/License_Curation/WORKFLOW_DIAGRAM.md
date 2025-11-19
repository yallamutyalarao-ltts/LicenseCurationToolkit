# Enhanced ORT Workflow - Complete Flow Diagrams

This document provides visual representations of the Enhanced ORT License Curation System workflow using Mermaid diagrams.

---

## Table of Contents

1. [Overall System Architecture](#overall-system-architecture)
2. [GitHub Actions Workflow](#github-actions-workflow)
3. [Multi-Tool Analysis Pipeline](#multi-tool-analysis-pipeline)
4. [AI Curation Decision Tree](#ai-curation-decision-tree)
5. [Report Generation Flow](#report-generation-flow)
6. [Deployment Pipeline](#deployment-pipeline)

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

## GitHub Actions Workflow

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

## Multi-Tool Analysis Pipeline

### Tier-Based License Detection

```mermaid
flowchart LR
    Source[Source Code<br/>Dependencies] --> Tier1{Tier 1:<br/>ORT Analyzer}

    Tier1 --> ORTResults[ORT Results<br/>Package Metadata<br/>Declared Licenses]
    ORTResults --> Check1{All Licenses<br/>Found?}

    Check1 -->|Yes - 100%| Success[✅ Complete<br/>All Licenses Known]
    Check1 -->|No - Gaps Found| Tier2{Tier 2:<br/>Extract Uncertain}

    Tier2 --> UncertainList[Uncertain Packages List<br/>NOASSERTION/UNKNOWN<br/>Empty Licenses]

    UncertainList --> Tier3{Tier 3:<br/>PyPI API Fetch}

    Tier3 --> PyPIFetch[PyPI API Calls<br/>Fast - No Scanning<br/>Multiple Metadata Sources]
    PyPIFetch --> PyPIResults[PyPI Results<br/>License Field<br/>License Expression<br/>Classifiers]

    PyPIResults --> Check2{More<br/>Licenses<br/>Found?}
    Check2 -->|Yes - 50-70%| Reduce[Reduced Uncertain List<br/>Remaining Packages]
    Check2 -->|No Improvement| Reduce

    Reduce --> Tier4{Tier 4:<br/>ScanCode Deep Scan}

    Tier4 --> ScanDeep[ScanCode Scanning<br/>File-Level Detection<br/>Package Manifest<br/>Source Files]
    ScanDeep --> ScanResults[ScanCode Results<br/>Package-Level License<br/>File-Level Licenses<br/>Confidence Scores]

    ScanResults --> Tier5{Tier 5:<br/>SPDX Merge}

    Tier5 --> MergeSPDX[Merge All Results<br/>ORT + PyPI + ScanCode<br/>High Confidence Only]
    MergeSPDX --> ValidateSPDX[Validate SPDX<br/>Fix Broken References<br/>Enhanced SPDX Document]

    ValidateSPDX --> Tier6{Tier 6:<br/>AI Curation}

    Tier6 --> AIAnalysis[AI-Powered Analysis<br/>Conflict Resolution<br/>Missing License Research<br/>Advisory Only]

    AIAnalysis --> Final{Final Step:<br/>Manual Review}

    Final --> ManualVerify[👤 Human Verification<br/>Check LICENSE Files<br/>Compliance Approval<br/>Add Curations]

    ManualVerify --> Complete[✅ 100% Coverage<br/>Production Ready]

    Success --> Complete

    style Source fill:#e3f2fd
    style Tier1 fill:#bbdefb
    style Tier2 fill:#90caf9
    style Tier3 fill:#64b5f6
    style Tier4 fill:#42a5f5
    style Tier5 fill:#2196f3
    style Tier6 fill:#1976d2
    style Final fill:#0d47a1
    style Complete fill:#4caf50,color:#fff
    style Success fill:#4caf50,color:#fff
```

---

## AI Curation Decision Tree

### AI Report Generation Logic

```mermaid
flowchart TD
    Start[AI Curation Stage] --> CheckKey{AZURE_OPENAI_API_KEY<br/>Secret Set?}

    CheckKey -->|No| Skip[❌ Skip All AI Reports<br/>Warning: API Key Missing]
    CheckKey -->|Yes| CheckEndpoint{AZURE_OPENAI_ENDPOINT<br/>Set?}

    CheckEndpoint -->|No| UseDefault[Use Default Endpoint<br/>ltts-cariad...azure.com]
    CheckEndpoint -->|Yes| UseCustom[Use Custom Endpoint]

    UseDefault --> CheckModel{AZURE_OPENAI_MODEL<br/>Set?}
    UseCustom --> CheckModel

    CheckModel -->|No| DefaultModel[Use Default:<br/>gpt-4.1-mini]
    CheckModel -->|Yes| CustomModel[Use Custom Model]

    DefaultModel --> Report1{Generate Report 1:<br/>Main ORT Curation}
    CustomModel --> Report1

    Report1 --> MainAI[Call Azure OpenAI<br/>Model: gpt-4.1-mini<br/>Comprehensive Analysis<br/>Max Tokens: 4000]

    MainAI --> MainSuccess{Success?}
    MainSuccess -->|Yes| SaveMain[✅ Save:<br/>curation-report-main.html]
    MainSuccess -->|No| ErrorMain[❌ Error:<br/>Log failure<br/>Continue anyway]

    SaveMain --> CheckUncertain{Uncertain<br/>Packages<br/>Exist?}
    ErrorMain --> CheckUncertain

    CheckUncertain -->|No| Report4
    CheckUncertain -->|Yes| Report2{Generate Report 2:<br/>Conflict Analysis}

    Report2 --> CheckSPDX{Enhanced SPDX<br/>Available?}
    CheckSPDX -->|No| SkipConflict[Skip Conflict Report<br/>Need ScanCode Results]
    CheckSPDX -->|Yes| ConflictAI[Call Azure OpenAI<br/>Model: gpt-4<br/>Analyze Conflicts<br/>Max: 20 conflicts]

    ConflictAI --> ConflictSuccess{Success?}
    ConflictSuccess -->|Yes| SaveConflict[✅ Save:<br/>curation-report-conflicts.html]
    ConflictSuccess -->|No| ErrorConflict[❌ Error:<br/>Log failure<br/>Continue anyway]

    SaveConflict --> Report3{Generate Report 3:<br/>Missing Licenses}
    ErrorConflict --> Report3
    SkipConflict --> Report3

    Report3 --> CheckMissing{Packages with<br/>NOASSERTION<br/>or Blank?}

    CheckMissing -->|No| Report4
    CheckMissing -->|Yes| MissingAI[Call Azure OpenAI<br/>Model: gpt-4o-mini<br/>Research Missing<br/>Max: 15 packages]

    MissingAI --> MissingSuccess{Success?}
    MissingSuccess -->|Yes| SaveMissing[✅ Save:<br/>curation-report-missing-licenses.html]
    MissingSuccess -->|No| ErrorMissing[❌ Error:<br/>Log failure<br/>Continue anyway]

    SaveMissing --> Report4{Generate Report 4:<br/>License Comparison}
    ErrorMissing --> Report4

    Report4 --> CompareLogic[Pure Comparison Logic<br/>No AI Required<br/>Compare ORT + PyPI + ScanCode]

    CompareLogic --> CompareSuccess{Success?}
    CompareSuccess -->|Yes| SaveCompare[✅ Save:<br/>license-comparison.html]
    CompareSuccess -->|No| ErrorCompare[❌ Error:<br/>Log failure<br/>Continue anyway]

    SaveCompare --> Report5{Generate Report 5:<br/>AI Multi-Layer Resolution}
    ErrorCompare --> Report5
    Skip --> Report4

    Report5 --> CheckAI2{Azure OpenAI<br/>Still Available?}

    CheckAI2 -->|No| SkipResolution[Skip AI Resolution<br/>API Key Missing]
    CheckAI2 -->|Yes| LoadData[Load Multi-Layer Data<br/>ORT + PyPI + ScanCode]

    LoadData --> CategorizeData[Categorize Packages:<br/>Resolved<br/>Conflicts<br/>Missing]

    CategorizeData --> CheckIssues{Conflicts or<br/>Missing<br/>Exist?}

    CheckIssues -->|No - All Resolved| OnlyResolved[Generate Report<br/>Show Only Resolved<br/>No AI Analysis Needed]
    CheckIssues -->|Yes| RunAI[Call Azure OpenAI<br/>Model: gpt-4.1-mini<br/>Analyze Conflicts: Max 15<br/>Analyze Missing: Max 10]

    OnlyResolved --> SaveResolution[✅ Save:<br/>ai-multilayer-resolution.html]
    RunAI --> ResolutionSuccess{Success?}

    ResolutionSuccess -->|Yes| SaveResolution
    ResolutionSuccess -->|No| ErrorResolution[❌ Error:<br/>Log failure<br/>Save partial report]

    ErrorResolution --> SaveResolution
    SkipResolution --> Done[Proceed to Deployment]
    SaveResolution --> Done

    Done --> End[AI Curation Complete]

    style Start fill:#9c27b0,color:#fff
    style End fill:#4caf50,color:#fff
    style Skip fill:#f44336,color:#fff
    style SaveMain fill:#4caf50,color:#fff
    style SaveConflict fill:#4caf50,color:#fff
    style SaveMissing fill:#4caf50,color:#fff
    style SaveCompare fill:#4caf50,color:#fff
    style SaveResolution fill:#4caf50,color:#fff
    style ErrorMain fill:#ff9800,color:#fff
    style ErrorConflict fill:#ff9800,color:#fff
    style ErrorMissing fill:#ff9800,color:#fff
    style ErrorCompare fill:#ff9800,color:#fff
    style ErrorResolution fill:#ff9800,color:#fff
```

---

## Report Generation Flow

### All Report Types

```mermaid
flowchart LR
    subgraph ORT_Reports[ORT Native Reports]
        ORT1[WebApp Report<br/>Interactive HTML]
        ORT2[Static HTML Report<br/>Traditional Format]
        ORT3[SPDX Document<br/>bom.spdx.yml]
        ORT4[CycloneDX SBOM<br/>bom.cyclonedx.json]
    end

    subgraph PyPI_Reports[PyPI API Reports NEW]
        PyPI1[PyPI Full JSON<br/>All Packages]
        PyPI2[PyPI Found JSON<br/>Licenses Found Only]
        PyPI3[PyPI CSV<br/>Spreadsheet Format]
        PyPI4[PyPI HTML Report<br/>Human Readable]
        PyPI5[Curation Suggestions<br/>YAML Format]
    end

    subgraph ScanCode_Reports[ScanCode Reports]
        Scan1[Individual HTML<br/>Per Package<br/>Native ScanCode]
        Scan2[Individual JSON<br/>Per Package<br/>Raw Data]
        Scan3[Individual YAML<br/>Per Package<br/>Raw Data]
        Scan4[Consolidated HTML<br/>All Packages<br/>Summary]
        Scan5[Consolidated YAML<br/>Machine Readable]
    end

    subgraph Enhanced_Reports[Enhanced/Merged Reports]
        Enh1[Enhanced SPDX<br/>ORT + ScanCode<br/>Merged]
        Enh2[Uncertain Packages MD<br/>Markdown Report]
        Enh3[Merge Report MD<br/>Statistics]
    end

    subgraph AI_Reports[AI-Powered Reports]
        AI1[Main ORT Curation<br/>gpt-4.1-mini<br/>Comprehensive]
        AI2[Conflict Analysis<br/>gpt-4<br/>ORT vs ScanCode]
        AI3[Missing Licenses<br/>gpt-4o-mini<br/>Research]
    end

    subgraph New_Reports[NEW Multi-Layer Reports]
        New1[License Comparison<br/>No AI<br/>Side-by-Side View]
        New2[AI Multi-Layer Resolution<br/>gpt-4.1-mini<br/>Resolved + Conflicts + Missing]
    end

    subgraph Landing[Landing Page]
        Index[index.html<br/>Auto-Generated<br/>Links to All Reports]
    end

    ORT_Reports --> Landing
    PyPI_Reports --> Landing
    ScanCode_Reports --> Landing
    Enhanced_Reports --> Landing
    AI_Reports --> Landing
    New_Reports --> Landing

    Landing --> GitHub[GitHub Pages<br/>https://username.github.io/repo/]

    style ORT_Reports fill:#e3f2fd
    style PyPI_Reports fill:#fff3e0
    style ScanCode_Reports fill:#f3e5f5
    style Enhanced_Reports fill:#e8f5e9
    style AI_Reports fill:#fce4ec
    style New_Reports fill:#fff9c4
    style Landing fill:#c8e6c9
    style GitHub fill:#4caf50,color:#fff
```

---

## Deployment Pipeline

### GitHub Pages Deployment Flow

```mermaid
flowchart TD
    Start[Stage 6: Prepare Deployment] --> CheckReports{Check Available<br/>Reports}

    CheckReports --> ORT{ORT Reports<br/>Exist?}
    ORT -->|Yes| CopyORT[Copy ORT Reports<br/>WebApp, Static HTML<br/>SPDX, CycloneDX]
    ORT -->|No| SkipORT[Skip ORT]

    CopyORT --> AI{AI Reports<br/>Exist?}
    SkipORT --> AI

    AI -->|Yes| CopyAI[Copy AI Reports<br/>Main, Conflicts<br/>Missing, Resolution]
    AI -->|No| SkipAI[Skip AI]

    CopyAI --> PyPI{PyPI Reports<br/>Exist?}
    SkipAI --> PyPI

    PyPI -->|Yes| CopyPyPI[Copy PyPI Reports<br/>HTML, JSON, CSV]
    PyPI -->|No| SkipPyPI[Skip PyPI]

    CopyPyPI --> Scan{ScanCode Reports<br/>Exist?}
    SkipPyPI --> Scan

    Scan -->|Yes| CopyScan[Copy ScanCode Reports<br/>Individual HTML/JSON/YAML<br/>Consolidated Reports]
    Scan -->|No| SkipScan[Skip ScanCode]

    CopyScan --> Enhanced{Enhanced Reports<br/>Exist?}
    SkipScan --> Enhanced

    Enhanced -->|Yes| CopyEnhanced[Copy Enhanced Reports<br/>Enhanced SPDX<br/>Merge Reports]
    Enhanced -->|No| SkipEnhanced[Skip Enhanced]

    CopyEnhanced --> Multi{Multi-Layer Reports<br/>Exist?}
    SkipEnhanced --> Multi

    Multi -->|Yes| CopyMulti[Copy Multi-Layer Reports<br/>License Comparison<br/>AI Resolution]
    Multi -->|No| SkipMulti[Skip Multi-Layer]

    CopyMulti --> Generate[Generate Landing Page<br/>Auto-Detect All Reports<br/>Create index.html]
    SkipMulti --> Generate

    Generate --> CheckBranch{Current Branch?}

    CheckBranch -->|main| Deploy[Deploy to Pages]
    CheckBranch -->|master| Deploy
    CheckBranch -->|Other| SkipDeploy[Skip Deployment<br/>Only for main/master]

    Deploy --> SetupPages[Setup GitHub Pages]
    SetupPages --> ConfigPages[Configure Pages<br/>Source: GitHub Actions]
    ConfigPages --> UploadArtifact[Upload Pages Artifact<br/>public/ directory]
    UploadArtifact --> DeployAction[Deploy Pages Action<br/>Publish to GitHub Pages]

    DeployAction --> Verify{Deployment<br/>Successful?}

    Verify -->|Yes| Success[✅ Deployment Complete<br/>Reports Live]
    Verify -->|No| Fail[❌ Deployment Failed<br/>Check Logs]

    Success --> URL[📍 Reports Available At:<br/>https://username.github.io/repo/]

    SkipDeploy --> Artifacts[Upload Artifacts Only<br/>30 Days Retention]
    Fail --> Artifacts

    Artifacts --> End[Workflow Complete]
    URL --> End

    style Start fill:#00bcd4,color:#fff
    style Deploy fill:#4caf50,color:#fff
    style Success fill:#4caf50,color:#fff
    style URL fill:#8bc34a,color:#fff
    style Fail fill:#f44336,color:#fff
    style SkipDeploy fill:#ff9800,color:#fff
    style End fill:#607d8b,color:#fff
```

---

## Parallel vs Sequential Execution

### Workflow Execution Strategy

```mermaid
gantt
    title Enhanced ORT Workflow - Execution Timeline
    dateFormat  mm:ss
    axisFormat %M:%S

    section Stage 1 ORT
    Install ORT           :done, ort1, 00:00, 01:00
    ORT Analyzer         :done, ort2, 01:00, 04:00
    ORT Advisor          :done, ort3, 04:00, 02:00
    ORT Reporter         :done, ort4, 06:00, 02:00

    section Stage 2-3 Extract & Scan
    Extract Uncertain    :done, ext1, 08:00, 00:30
    PyPI API Fetch       :done, pypi1, 08:30, 01:00
    Download Packages    :done, down1, 09:30, 02:00
    ScanCode Scan        :done, scan1, 11:30, 08:00

    section Stage 4 Merge
    Consolidate Reports  :done, cons1, 19:30, 00:30
    Merge to SPDX        :done, merge1, 20:00, 00:30
    Validate SPDX        :done, val1, 20:30, 00:30

    section Stage 5 AI (Parallel)
    Main AI Report       :done, ai1, 21:00, 01:00
    Conflict Analysis    :done, ai2, 21:00, 01:30
    Missing Licenses     :done, ai3, 21:00, 01:00
    License Comparison   :done, comp1, 22:00, 00:30
    AI Resolution        :done, res1, 22:30, 01:30

    section Stage 6-7 Deploy
    Prepare Public       :done, prep1, 24:00, 00:30
    Generate Landing     :done, land1, 24:30, 00:15
    Deploy Pages         :done, deploy1, 24:45, 01:00
    Upload Artifacts     :done, art1, 25:45, 00:30
```

**Key Observations:**
- **Sequential:** ORT stages must run in order (Analyzer → Advisor → Reporter)
- **Sequential:** ScanCode depends on uncertain packages extraction
- **Parallel:** AI reports can run simultaneously (except AI Resolution depends on Comparison)
- **Total Time:** ~26-30 minutes for complete workflow

---

## Error Handling Flow

### Continue-on-Error Strategy

```mermaid
flowchart TD
    Start[Workflow Stage] --> Execute[Execute Stage]

    Execute --> Check{Stage<br/>Success?}

    Check -->|Success| Required{Is Stage<br/>Required?}
    Check -->|Failure| Required

    Required -->|Yes - Critical| StopWorkflow[❌ Stop Workflow<br/>Mark as Failed<br/>Send Notifications]
    Required -->|No - Optional| LogError[⚠️ Log Error<br/>Set continue-on-error: true<br/>Continue to Next Stage]

    StopWorkflow --> End[Workflow Failed]

    LogError --> CheckDependents{Are There<br/>Dependent<br/>Stages?}

    CheckDependents -->|Yes| SkipDependents[Skip Dependent Stages<br/>Mark as Skipped<br/>Show Warning]
    CheckDependents -->|No| NextStage[Continue to Next Stage]

    SkipDependents --> NextStage
    NextStage --> Check2{More Stages?}

    Check2 -->|Yes| Execute
    Check2 -->|No| FinalCheck{Any Critical<br/>Failures?}

    FinalCheck -->|Yes| FailureEnd[Workflow Failed<br/>Some Reports Generated]
    FinalCheck -->|No| SuccessEnd[✅ Workflow Success<br/>All/Most Reports Generated]

    Required -->|Success| NextStage

    style Start fill:#2196f3,color:#fff
    style StopWorkflow fill:#f44336,color:#fff
    style LogError fill:#ff9800,color:#fff
    style FailureEnd fill:#f44336,color:#fff
    style SuccessEnd fill:#4caf50,color:#fff
    style End fill:#607d8b,color:#fff
```

**Stages with continue-on-error: true:**
- ✅ ORT Advisor (optional vulnerability scanning)
- ✅ ScanCode Scanning (optional deep analysis)
- ✅ All AI Reports (optional AI analysis)
- ✅ GitHub Pages Deployment (not available on PRs)

**Stages that MUST succeed:**
- ❌ ORT Analyzer (critical - base dependency analysis)
- ❌ Install dependencies (critical - setup)

---

## Cost Optimization Flow

### AI Usage and Cost Control

```mermaid
flowchart TD
    Start[AI Curation Stage] --> CheckKey{API Key<br/>Available?}

    CheckKey -->|No| Free[Use Free Features Only<br/>Skip AI<br/>$0 USD]
    CheckKey -->|Yes| Report1[Main ORT Report<br/>gpt-4.1-mini<br/>Always Runs]

    Report1 --> Cost1[Cost: ~$0.05]

    Cost1 --> CheckUncertain{Uncertain<br/>Packages?}

    CheckUncertain -->|No| Cost2[Total: $0.05<br/>Skip Other AI Reports]
    CheckUncertain -->|Yes| CountConflicts{Count<br/>Conflicts}

    CountConflicts --> HasConflicts{Conflicts<br/>> 0?}

    HasConflicts -->|Yes| LimitConflicts{Conflicts<br/>> 20?}
    HasConflicts -->|No| CheckMissing

    LimitConflicts -->|Yes| Limit20[Analyze First 20<br/>Cost Control]
    LimitConflicts -->|No| AnalyzeAll[Analyze All Conflicts]

    Limit20 --> Report2[Conflict Report<br/>gpt-4<br/>Max 20]
    AnalyzeAll --> Report2

    Report2 --> Cost3[Cost: ~$0.10-$0.20]

    Cost3 --> CheckMissing{Missing<br/>Licenses?}

    CheckMissing -->|No| MultiLayer
    CheckMissing -->|Yes| LimitMissing{Missing<br/>> 15?}

    LimitMissing -->|Yes| Limit15[Analyze First 15<br/>Cost Control]
    LimitMissing -->|No| AnalyzeAllMiss[Analyze All Missing]

    Limit15 --> Report3[Missing Report<br/>gpt-4o-mini<br/>Max 15]
    AnalyzeAllMiss --> Report3

    Report3 --> Cost4[Cost: ~$0.05-$0.08]

    Cost4 --> MultiLayer{Multi-Layer<br/>Resolution?}

    MultiLayer -->|Skip| Cost5[Total: $0.20-$0.33]
    MultiLayer -->|Include| LimitResolution{Issues<br/>> 25?}

    LimitResolution -->|Yes| Limit25[Analyze:<br/>15 Conflicts<br/>10 Missing]
    LimitResolution -->|No| AnalyzeAllRes[Analyze All Issues]

    Limit25 --> Report4[Resolution Report<br/>gpt-4.1-mini<br/>Max 25]
    AnalyzeAllRes --> Report4

    Report4 --> Cost6[Cost: ~$0.08-$0.12]

    Cost6 --> Total[Total: $0.28-$0.45]

    Cost2 --> Monthly
    Cost5 --> Monthly
    Total --> Monthly{Run<br/>Frequency?}

    Monthly -->|Daily| Daily[Daily: $0.28-$0.45<br/>Monthly: ~$8-$14]
    Monthly -->|Weekly| Weekly[Weekly: $0.28-$0.45<br/>Monthly: ~$1-$2]
    Monthly -->|On Push| OnDemand[On-Demand Only<br/>Variable Cost]

    Free --> End[Workflow Complete<br/>$0 USD]
    Daily --> End
    Weekly --> End
    OnDemand --> End

    style Start fill:#9c27b0,color:#fff
    style Free fill:#4caf50,color:#fff
    style Cost1 fill:#fff9c4
    style Cost2 fill:#fff9c4
    style Cost3 fill:#ffe0b2
    style Cost4 fill:#ffe0b2
    style Cost5 fill:#ffccbc
    style Cost6 fill:#ffccbc
    style Total fill:#ff8a65,color:#fff
    style Daily fill:#ff5722,color:#fff
    style Weekly fill:#8bc34a,color:#fff
    style OnDemand fill:#2196f3,color:#fff
    style End fill:#607d8b,color:#fff
```

---

## Summary

This workflow documentation provides complete visual representations of:

1. **Overall System Architecture** - High-level system flow
2. **GitHub Actions Workflow** - Detailed CI/CD pipeline with all stages
3. **Multi-Tool Analysis Pipeline** - 6-tier license detection approach
4. **AI Curation Decision Tree** - AI report generation logic and fallbacks
5. **Report Generation Flow** - All 13+ report types and relationships
6. **Deployment Pipeline** - GitHub Pages deployment process
7. **Parallel vs Sequential Execution** - Timing and execution strategy
8. **Error Handling Flow** - Continue-on-error strategy
9. **Cost Optimization Flow** - AI usage limits and cost control

### Key Features:

- ✅ **Visual Clarity** - Mermaid diagrams for easy understanding
- ✅ **Decision Points** - Shows all conditional logic
- ✅ **Error Handling** - Continue-on-error and fallback paths
- ✅ **Cost Control** - AI usage limits clearly shown
- ✅ **Parallel Execution** - Shows which stages can run simultaneously
- ✅ **Complete Coverage** - All 8 workflow stages documented

### Usage:

These diagrams can be viewed:
- **In GitHub** - Mermaid is natively supported in GitHub markdown
- **In VS Code** - With Mermaid preview extension
- **Online** - At https://mermaid.live/ (paste diagram code)
- **In Documentation** - Renders in most modern markdown viewers

---

**Last Updated:** 2025-01-15
**Version:** 2.0 - Multi-Layer Resolution Enhancement
**Diagrams:** 9 comprehensive flow diagrams
