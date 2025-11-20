# Publishing ConanX to PyPI

This guide explains how to build, test, and publish the ConanX package to PyPI.

## Prerequisites

1. **Install build tools:**
```bash
pip install --upgrade build twine
```

2. **Create PyPI account:**
   - Sign up at https://pypi.org/account/register/
   - Enable 2FA (recommended)
   - Create an API token at https://pypi.org/manage/account/token/

3. **Create TestPyPI account (for testing):**
   - Sign up at https://test.pypi.org/account/register/
   - Create an API token

## Local Testing

### 1. Install in Development Mode

From the `conanx_package` directory:

```bash
pip install -e .
```

This installs the package in "editable" mode, allowing you to make changes and test them immediately.

### 2. Test the CLI

```bash
# Test basic command
conanx --help

# Test specific commands
conanx init --help
conanx setup --help
```

### 3. Test with Python

```python
from conanx import main
# Test imports work
```

### 4. Uninstall Development Version

```bash
pip uninstall conanx
```

## Building the Package

### 1. Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info
# or on Windows:
rmdir /s /q build dist
del /s /q *.egg-info
```

### 2. Build Distribution Files

```bash
python -m build
```

This creates:
- `dist/conanx-1.0.0.tar.gz` (source distribution)
- `dist/conanx-1.0.0-py3-none-any.whl` (wheel distribution)

### 3. Check Package

```bash
twine check dist/*
```

This validates your package metadata and descriptions.

## Testing on TestPyPI (Recommended)

Before publishing to the real PyPI, test on TestPyPI:

### 1. Upload to TestPyPI

```bash
twine upload --repository testpypi dist/*
```

You'll be prompted for your TestPyPI credentials:
- Username: `__token__`
- Password: Your TestPyPI API token (including the `pypi-` prefix)

### 2. Test Installation from TestPyPI

```bash
# Create a test virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ conanx

# Test the command
conanx --help

# Deactivate and remove test environment
deactivate
rm -rf test_env  # On Windows: rmdir /s /q test_env
```

Note: We need `--extra-index-url https://pypi.org/simple/` because dependencies (conan, click, requests) are on PyPI, not TestPyPI.

## Publishing to PyPI

Once you've tested everything:

### 1. Upload to PyPI

```bash
twine upload dist/*
```

You'll be prompted for your PyPI credentials:
- Username: `__token__`
- Password: Your PyPI API token (including the `pypi-` prefix)

### 2. Verify Installation

```bash
# Create a fresh virtual environment
python -m venv verify_env
source verify_env/bin/activate  # On Windows: verify_env\Scripts\activate

# Install from PyPI
pip install conanx

# Test it works
conanx --help

# Clean up
deactivate
rm -rf verify_env  # On Windows: rmdir /s /q verify_env
```

## Using .pypirc for Authentication

To avoid entering credentials repeatedly, create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YourRealPyPITokenHere

[testpypi]
username = __token__
password = pypi-YourTestPyPITokenHere
```

**Security Note:** Make sure this file has restricted permissions:
```bash
chmod 600 ~/.pypirc
```

## Versioning

Update version numbers in:
1. `pyproject.toml` - `version = "x.y.z"`
2. `conanx/__init__.py` - `__version__ = "x.y.z"`

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.0.1): Bug fixes

## Release Checklist

Before each release:

- [ ] Update version in `pyproject.toml` and `conanx/__init__.py`
- [ ] Update CHANGELOG.md (if you have one)
- [ ] Run tests locally
- [ ] Clean old build artifacts
- [ ] Build new distributions
- [ ] Check package with `twine check`
- [ ] Upload to TestPyPI and test
- [ ] Upload to PyPI
- [ ] Create Git tag: `git tag v1.0.0 && git push --tags`
- [ ] Create GitHub release (if applicable)

## Troubleshooting

### Package Already Exists

PyPI doesn't allow re-uploading the same version. You must:
1. Increment the version number
2. Rebuild the package
3. Upload again

### Import Errors After Installation

Make sure:
- Package structure is correct
- `__init__.py` files exist
- Entry points are properly defined in `pyproject.toml`

### Command Not Found

After installation, if `conanx` command is not found:
1. Check if Python scripts directory is in PATH
2. Try: `python -m conanx` as an alternative
3. Reinstall: `pip install --force-reinstall conanx`

## Updating the Package

When you make changes:

1. Update version number
2. Clean and rebuild:
   ```bash
   rm -rf dist/ build/ *.egg-info
   python -m build
   ```
3. Test on TestPyPI first
4. Upload to PyPI

## Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [PEP 517/518](https://peps.python.org/pep-0517/) - Modern Python packaging
