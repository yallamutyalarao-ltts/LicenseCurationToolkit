# Changelog

All notable changes to the License Curation Toolkit.

## [2025-11-29] - Bug Fixes

### Fixed
- **Multi-Layer License Comparison Report not generating**
  - **Root Cause:** Empty or invalid SPDX JSON file causing `JSONDecodeError`
  - **Fix:** Added comprehensive error handling for SPDX file loading
  - **Impact:** Report now generates successfully even when SPDX data is unavailable

- **Division by zero errors in report generation**
  - Added safety checks for percentage calculations when no packages are found

- **Script crash on malformed data**
  - Implemented graceful degradation for all data source loading
  - Each source (ORT, PyPI, ScanCode, SPDX) now handles errors independently

### Enhanced
- **Better error messages**
  - Scripts now show detailed error information instead of silent failures
  - Traceback included for debugging

- **Improved resilience**
  - Workflow continues even if individual data sources fail
  - Reports generate with available data

## [2025-11-28] - Repository Cleanup

### Removed
- `LicenseCurationTool-main/` directory (redundant files)
- Duplicate `.drawio` files from root directory

### Added
- `README.md` - Quick start guide
- `DEPLOYMENT.md` - Deployment instructions
- `QUICK_START_CHECKLIST.md` - Step-by-step checklist
- `CLEANUP_SUMMARY.md` - Cleanup documentation
- `FINAL_SUMMARY.md` - Repository overview
- `TROUBLESHOOTING_GITHUB_PAGES.md` - Debugging guide
- `.gitignore` - Comprehensive ignore patterns
- `verify_setup.sh` - Automated verification script

### Changed
- Restructured repository for multi-repo deployment
- Improved documentation organization
- Enhanced workflow comments and structure

## Files Modified

### workflow_components/scripts/generate_license_comparison.py
- Added error handling for empty/invalid SPDX files
- Fixed division by zero in percentage calculations
- Added top-level exception handling with stack traces
- Implemented graceful degradation for data source failures

## Migration Guide

If upgrading from an older version:

1. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

2. **The fixes are backward compatible** - no workflow changes needed

3. **Re-run your workflow** to benefit from the improvements

## Known Issues

- SPDX file may be empty in some configurations (handled gracefully now)
- ScanCode timeout may occur for very large projects (configurable limit: 20 packages)

## Next Release

Planned improvements:
- Enhanced SPDX generation robustness
- Configurable timeout for ScanCode
- Additional data source integrations
