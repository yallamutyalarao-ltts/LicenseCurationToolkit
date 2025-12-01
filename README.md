# License Curation Toolkit

A comprehensive, production-ready solution for automated license compliance using ORT (OSS Review Toolkit) with advanced policy enforcement, change monitoring, and AI-powered curation.

## Quick Start

This repository contains a complete license curation workflow that can be deployed to any project repository.

### Structure

```
LicenseCurationToolkit/
├── .github/
│   └── workflows/
│       └── advanced-integrated-workflow.yml    # Main workflow file
├── workflow_components/                         # Core components (deploy this)
│   ├── config/
│   │   └── company-policy.yml                  # Customize your license policy
│   ├── scripts/                                # All automation scripts
│   │   ├── policy_checker.py
│   │   ├── license_change_monitor.py
│   │   ├── alternative_package_finder.py
│   │   ├── smart_curation_engine.py
│   │   ├── compliance_dashboard.py
│   │   ├── sbom_compliance_checker.py
│   │   └── ... (14 more scripts)
│   ├── docs/                                   # Documentation
│   └── README.md                               # Detailed component docs
└── sample_conanx_package/                      # Test package for verification
```

## Deployment to Your Repository

### 1. Copy Workflow Components

```bash
# From this repository, copy to your target repository:
cp -r workflow_components/ <your-repo>/
cp .github/workflows/advanced-integrated-workflow.yml <your-repo>/.github/workflows/
```

### 2. Configure Company Policy

Edit `workflow_components/config/company-policy.yml` to match your organization's requirements:

```yaml
company_license_policy:
  company_name: "Your Company Name"  # Change this

  approved_licenses:
    permissive:
      licenses:
        - "MIT"
        - "Apache-2.0"
        - "BSD-3-Clause"

  forbidden_licenses:
    proprietary_restricted:
      licenses:
        - "GPL-3.0-only"  # Add your forbidden licenses
        - "SSPL-1.0"
```

### 3. Set Up GitHub Secrets (Optional, for AI features)

Go to your repository Settings → Secrets → Actions and add:

- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint
- `AZURE_OPENAI_MODEL` - Your deployment name (optional)

### 4. Commit and Push

```bash
cd <your-repo>
git add .github/workflows/advanced-integrated-workflow.yml workflow_components/
git commit -m "Add advanced license curation workflow"
git push
```

## Features

### Policy Enforcement
- Automatic policy compliance checking
- Approved/Conditional/Forbidden license categorization
- Compliance scoring (0-100%)
- Build fails on policy violations

### License Change Monitoring
- Historical tracking database
- Severity assessment (CRITICAL/HIGH/MEDIUM/LOW)
- Detects permissive → copyleft changes
- Automated alerts

### Alternative Package Finder
- Automatic search for compliant alternatives
- Multi-factor ranking (license, popularity, maintenance)
- Side-by-side comparison reports

### Multi-Source License Detection
1. ORT Analyzer - Package manager metadata
2. Policy Checker - Company policy enforcement
3. PyPI API - Fast registry lookup
4. ScanCode - Deep source code scanning
5. Smart Curation Engine - Multi-source evidence aggregation
6. AI Analysis - Intelligent conflict resolution (optional)

### SBOM & Compliance
- Official SPDX validation (spdx-tools)
- NTIA minimum elements validation
- Multi-format export (JSON, YAML, Tag-Value, RDF)
- Compliance scoring
- US Executive Order 14028 compliant

### Reports Generated
- Policy compliance report (HTML + JSON)
- License change alerts with severity
- NTIA SBOM compliance report
- Multi-format SPDX export
- Alternative packages report
- Smart curation review queue
- Unified compliance dashboard
- Interactive GitHub Pages deployment

## Workflow Triggers

The workflow runs automatically on:
- Every push to `main`/`master`/`develop`
- Every pull request
- Daily at 2 AM UTC (for license change monitoring)
- Manual trigger via `workflow_dispatch`

## Testing

Test the workflow with the included sample package:

```bash
cd sample_conanx_package
# Follow the instructions in sample_conanx_package/README.md
```

## Documentation

- **[workflow_components/README.md](workflow_components/README.md)** - Complete component documentation
- **[workflow_components/docs/QUICK_SETUP.md](workflow_components/docs/QUICK_SETUP.md)** - 15-minute setup guide
- **[workflow_components/docs/WORKFLOW_STRUCTURE.md](workflow_components/docs/WORKFLOW_STRUCTURE.md)** - Architecture details

## Requirements

### GitHub Actions Environment (Automatic)
- Python 3.11+
- Java 21 (for ORT)
- ORT 70.0.1+ (auto-installed)
- All Python dependencies (auto-installed)

### Local Development
```bash
pip install pyyaml requests spdx-tools scancode-toolkit python-inspector openai
```

## Support

For issues, questions, or contributions:
1. Check the [workflow_components/README.md](workflow_components/README.md) documentation
2. Review the troubleshooting section
3. Open an issue with detailed information

## License

Apache-2.0

## Made for Software Compliance Teams

This toolkit helps organizations maintain license compliance, track changes, and make informed decisions about open source dependencies.

Last Updated: 2025-11-28
