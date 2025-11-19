# Azure OpenAI Deployment Fix Summary

## Problem

The AI Multi-Layer Resolution report was failing with `DeploymentNotFound` errors:
```
Error code: 404 - {'error': {'code': 'DeploymentNotFound',
'message': 'The API deployment for this resource does not exist.'}}
```

**Root Cause:** The script was using `gpt-4o-mini` deployment name, but your Azure Portal has the deployment named `gpt-4.1-mini`.

## Solution

Updated all scripts and configurations to use `gpt-4.1-mini` as the default deployment name, matching your working `ort_curation_script_html.py`.

## Files Changed

### 1. `ai_multilayer_resolution.py`
**Changes:**
- Line 55: Added default endpoint fallback
- Line 56: Changed default from `gpt-4o-mini` → `gpt-4.1-mini`
- Line 69: Updated API version from `2024-08-01-preview` → `2025-01-01-preview`

**Before:**
```python
endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
self.model_deployment = os.environ.get('AZURE_OPENAI_MODEL', 'gpt-4o-mini')
api_version="2024-08-01-preview"
```

**After:**
```python
endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT', 'https://ltts-cariad-ddd-mvp-ai-foundry.cognitiveservices.azure.com')
self.model_deployment = os.environ.get('AZURE_OPENAI_MODEL', 'gpt-4.1-mini')
api_version="2025-01-01-preview"
```

### 2. `enhanced-ort-workflow.yml`
**Changes:**
- Line 541: Changed workflow default from `gpt-4o-mini` → `gpt-4.1-mini`

**Before:**
```yaml
AZURE_OPENAI_MODEL: ${{ secrets.AZURE_OPENAI_MODEL || 'gpt-4o-mini' }}
```

**After:**
```yaml
AZURE_OPENAI_MODEL: ${{ secrets.AZURE_OPENAI_MODEL || 'gpt-4.1-mini' }}
```

### 3. Documentation Updates

**`AZURE_OPENAI_SETUP.md`:**
- Updated recommended deployment name to `gpt-4.1-mini`
- Added API version information
- Updated example values

**`CLAUDE.md`:**
- Added AI Multi-Layer Resolution configuration section
- Documented API version and deployment settings

### 4. New Testing Files

Created quick testing tools:

1. **`test_azure_openai.py`** - Python test script
   - Validates Azure OpenAI configuration
   - Tests connection and model deployment
   - Provides troubleshooting guidance

2. **`test_azure_openai.bat`** - Windows CMD launcher

3. **`setup_test_env.bat`** - Windows CMD setup script
   - Sets environment variables automatically
   - Runs configuration test
   - Shows next steps

4. **`setup_test_env.ps1`** - PowerShell setup script
   - Same functionality for PowerShell users

5. **`LOCAL_TEST.md`** - Complete testing guide
   - Step-by-step local testing instructions
   - Troubleshooting reference
   - GitHub secrets setup guide

6. **`FIX_SUMMARY.md`** - This file

## How to Test Locally

### Quick Test (Windows)

**Option 1: Command Prompt**
```cmd
setup_test_env.bat
```

**Option 2: PowerShell**
```powershell
.\setup_test_env.ps1
```

### Manual Test

1. Set environment variables:
```cmd
set AZURE_OPENAI_API_KEY=6CwE55InRG2OQa59XCrGSjqMX1RmvXDqrNoD4w2MiGWl7nUxUgxYJQQJ99BIAC77bzfXJ3w3AAAAACOGEovm
set AZURE_OPENAI_ENDPOINT=https://ltts-cariad-ddd-mvp-ai-foundry.cognitiveservices.azure.com
set AZURE_OPENAI_MODEL=gpt-4.1-mini
```

2. Run test:
```cmd
python test_azure_openai.py
```

3. If test passes, run the full script:
```cmd
python ai_multilayer_resolution.py --ort-result ort-results/analyzer/analyzer-result.yml --pypi-results pypi-licenses/pypi-licenses-full.json --scancode-dir scancode-results --uncertain-packages uncertain-packages/uncertain-packages.json --output ai-multilayer-resolution.html
```

## Expected Results

### Before Fix
```
✓ Azure OpenAI client initialized
  Using model deployment: gpt-4o-mini  ❌ WRONG!

⚠️  AI analysis failed for docutils: Error code: 404 - DeploymentNotFound
```

### After Fix
```
✓ Azure OpenAI client initialized
  Using model deployment: gpt-4.1-mini  ✅ CORRECT!

🤖 Running AI analysis on problematic packages...
   Analyzing 1 conflict packages...
      [1/1] docutils
   ✓ AI analysis completed

✅ Report generated: ai-multilayer-resolution.html
```

## GitHub Configuration

The workflow will now work correctly even **without** setting the `AZURE_OPENAI_MODEL` secret in GitHub, because it defaults to `gpt-4.1-mini`.

However, if you want to use a different deployment, you can override it:

1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Add secret:
   - Name: `AZURE_OPENAI_MODEL`
   - Value: Your custom deployment name

## Consistency Across All Scripts

All AI-powered scripts now use consistent configuration:

| Script | API Version | Default Deployment | Configurable? |
|--------|-------------|-------------------|---------------|
| `ort_curation_script_html.py` | `2025-01-01-preview` | `gpt-4.1-mini` | No (hardcoded) |
| `ai_multilayer_resolution.py` | `2025-01-01-preview` | `gpt-4.1-mini` | Yes (env var) |
| `enhanced_ai_curation.py` | TBD | `gpt-4` | TBD |
| `ai_missing_licenses_analyzer.py` | TBD | `gpt-4o-mini` | TBD |

**Note:** Other AI scripts (`enhanced_ai_curation.py` and `ai_missing_licenses_analyzer.py`) may need similar updates if they also fail. Check their configuration if you encounter issues.

## Verification Checklist

- [x] `ai_multilayer_resolution.py` updated to use `gpt-4.1-mini` default
- [x] API version updated to `2025-01-01-preview`
- [x] Workflow default changed to `gpt-4.1-mini`
- [x] Test scripts created for local validation
- [x] Documentation updated
- [ ] Test locally with `setup_test_env.bat` or `test_azure_openai.py`
- [ ] Verify AI analysis works without 404 errors
- [ ] Push changes to GitHub
- [ ] Verify GitHub Actions workflow runs successfully

## Next Steps

1. **Test locally first** using the setup scripts
2. **Verify the AI analysis completes** without DeploymentNotFound errors
3. **Commit and push** the changes to GitHub
4. **Monitor the GitHub Actions workflow** to ensure it works in CI/CD

## Support

If you still encounter issues:

1. Check `LOCAL_TEST.md` for detailed troubleshooting
2. Check `AZURE_OPENAI_SETUP.md` for Azure Portal setup
3. Verify your deployment name in Azure Portal exactly matches `gpt-4.1-mini`
4. Ensure API version `2025-01-01-preview` is supported by your Azure resource

## Summary

✅ **Fixed:** Default deployment name matches Azure Portal (`gpt-4.1-mini`)
✅ **Fixed:** API version updated to current version (`2025-01-01-preview`)
✅ **Fixed:** Workflow uses correct default
✅ **Added:** Local testing tools for quick validation
✅ **Added:** Comprehensive documentation

The AI Multi-Layer Resolution report should now work correctly! 🎉
