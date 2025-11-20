# ConanX Package - Quick Start Guide

## 🎉 Your package is ready!

The `conanx` CLI tool has been successfully converted into a proper Python package that can be installed via pip and run as `conanx` instead of `python runConan.py`.

## 📦 What's Been Created

```
conanx_package/
├── conanx/              # Main package with your CLI code
├── pyproject.toml       # Package configuration
├── README.md            # Updated with pip install instructions
├── LICENSE              # MIT License
├── PUBLISHING_GUIDE.md  # Detailed publishing instructions
├── PACKAGE_STRUCTURE.md # Package structure documentation
├── build.sh / build.bat # Build scripts
└── test_install.py      # Installation test script
```

## 🚀 Quick Start

### Step 1: Test Locally

```bash
cd conanx_package

# Install in development mode
pip install -e .

# Test the command
conanx --help
conanx init --help
```

### Step 2: Build the Package

**On Linux/Mac:**
```bash
./build.sh
```

**On Windows:**
```bash
build.bat
```

**Or manually:**
```bash
# Install build tools first (one time)
pip install --upgrade build twine

# Clean and build
rm -rf dist/ build/ *.egg-info  # On Windows: use rmdir and del
python -m build
twine check dist/*
```

### Step 3: Test the Package

After building, test the installation:

```bash
# Create a test environment
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# Install from local build
pip install dist/conanx-1.0.0-py3-none-any.whl

# Test it works
conanx --help
conanx setup --help

# Run test suite
python test_install.py

# Clean up
deactivate
rm -rf test_env
```

## 📤 Publishing to PyPI

### Option 1: Test on TestPyPI First (Recommended)

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ conanx
```

### Option 2: Publish to Real PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Users can now install with:
pip install conanx
```

**Note:** You'll need:
- A PyPI account (https://pypi.org/account/register/)
- An API token (https://pypi.org/manage/account/token/)
- Use `__token__` as username and your token as password

## 🎯 Usage After Installation

Once published and installed, users can:

```bash
# Install
pip install conanx

# Use the CLI
conanx setup --remote conan_test
conanx init mypackage 1.0.0 source_folder
conanx create
conanx install
conanx check
```

## 📝 Before Publishing Checklist

- [ ] Update your email in `pyproject.toml`
- [ ] Update GitHub URLs in `pyproject.toml` (or remove them)
- [ ] Test installation locally
- [ ] Run `python test_install.py` successfully
- [ ] Create PyPI account
- [ ] Generate PyPI API token
- [ ] Test on TestPyPI first
- [ ] Then publish to real PyPI

## 🔄 Updating the Package

When you make changes:

1. **Update version** in both:
   - `pyproject.toml`: `version = "1.0.1"`
   - `conanx/__init__.py`: `__version__ = "1.0.1"`

2. **Rebuild:**
   ```bash
   rm -rf dist/ build/ *.egg-info
   python -m build
   ```

3. **Republish:**
   ```bash
   twine upload dist/*
   ```

## 📚 Documentation

- **PUBLISHING_GUIDE.md** - Detailed publishing instructions
- **PACKAGE_STRUCTURE.md** - Package structure explanation
- **README.md** - User documentation (updated with pip install)

## 🆘 Troubleshooting

### "conanx: command not found"

```bash
# Check if installed
pip show conanx

# Check if Python scripts directory is in PATH
python -m site

# Alternative: use python -m
python -m conanx --help
```

### "Module not found" errors

```bash
# Reinstall
pip uninstall conanx
pip install conanx
```

### Package name already exists on PyPI

If "conanx" is taken, update the name in:
- `pyproject.toml`: `name = "your-new-name"`
- Rebuild and republish

## 🎓 Next Steps

1. ✅ Test locally with `pip install -e .`
2. ✅ Build with `./build.sh` or `build.bat`
3. ✅ Test with `python test_install.py`
4. ✅ Create PyPI account
5. ✅ Test on TestPyPI
6. ✅ Publish to PyPI
7. ✅ Share with users: `pip install conanx`

## 📞 Support

For detailed instructions, see:
- `PUBLISHING_GUIDE.md` - Complete publishing guide
- `PACKAGE_STRUCTURE.md` - Technical details
- PyPI documentation: https://packaging.python.org/

---

**Congratulations! Your CLI is now a proper Python package! 🎊**
