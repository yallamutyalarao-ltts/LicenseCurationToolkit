# ConanX Package Structure

This document explains the structure of the ConanX Python package.

## Directory Structure

```
conanx_package/
├── conanx/                    # Main package directory
│   ├── __init__.py           # Package initialization, exports main()
│   ├── __main__.py           # Enables 'python -m conanx'
│   └── cli.py                # Main CLI implementation (from runConan.py)
│
├── build/                     # Build artifacts (generated, gitignored)
├── dist/                      # Distribution files (generated, gitignored)
├── *.egg-info/               # Package metadata (generated, gitignored)
│
├── pyproject.toml            # Modern Python package configuration
├── MANIFEST.in               # Specifies which files to include in dist
├── LICENSE                   # MIT License
├── README.md                 # User documentation
├── .gitignore                # Git ignore rules
│
├── PUBLISHING_GUIDE.md       # How to publish to PyPI
├── PACKAGE_STRUCTURE.md      # This file
├── build.sh                  # Build script for Linux/Mac
├── build.bat                 # Build script for Windows
└── test_install.py           # Installation verification script
```

## Key Files

### pyproject.toml

Modern Python packaging configuration file (PEP 517/518). Defines:
- Package metadata (name, version, description, author)
- Dependencies
- Entry points (CLI commands)
- Build system requirements

**Entry Point:**
```toml
[project.scripts]
conanx = "conanx.cli:main"
```

This creates the `conanx` command that calls `main()` from `conanx/cli.py`.

### conanx/__init__.py

Package initialization file. Exports:
- `main()` function for CLI entry point
- `__version__` for version information
- `__author__` for author information

### conanx/cli.py

The main CLI implementation, converted from the original `runConan.py`. Contains:
- `ConanClient` class for Conan operations
- All Click command definitions
- `main()` function as the entry point

### conanx/__main__.py

Enables running the package with `python -m conanx`. Simply calls `main()` from cli.py.

## How It Works

When a user installs the package:

1. `pip install conanx` downloads and installs the package
2. The entry point in `pyproject.toml` creates a `conanx` executable
3. Running `conanx` calls `conanx.cli:main()`
4. The `main()` function calls `cli()` which is the Click command group
5. Click handles argument parsing and command routing

## Development Workflow

### Local Development

```bash
# Install in editable mode
cd conanx_package
pip install -e .

# Make changes to conanx/cli.py
# Test immediately
conanx --help
```

### Building for Distribution

```bash
# Option 1: Use build script
./build.sh        # Linux/Mac
build.bat         # Windows

# Option 2: Manual build
python -m build
twine check dist/*
```

### Testing

```bash
# Test imports
python -c "from conanx import main; print('OK')"

# Test CLI
conanx --help

# Run test suite
python test_install.py
```

## Version Management

Update version in TWO places:
1. `pyproject.toml`: `version = "1.0.0"`
2. `conanx/__init__.py`: `__version__ = "1.0.0"`

These should always match!

## Adding New Commands

To add a new command:

1. Edit `conanx/cli.py`
2. Add a new function decorated with `@cli.command()`
3. Test locally with `pip install -e .`
4. Update version and rebuild for distribution

Example:
```python
@cli.command()
@click.option('-f', '--flag')
def mycommand(flag):
    """My new command description"""
    click.echo(f"Running mycommand with flag: {flag}")
```

## Dependencies

Managed in `pyproject.toml`:

**Runtime dependencies:**
- conan>=2.0.0
- click>=8.0.0
- requests>=2.25.0

**Development dependencies (optional):**
- pytest>=7.0.0
- black>=22.0.0
- flake8>=4.0.0

Install dev dependencies:
```bash
pip install -e ".[dev]"
```

## Publishing

See `PUBLISHING_GUIDE.md` for detailed instructions on:
- Testing locally
- Publishing to TestPyPI
- Publishing to PyPI
- Version management
- Release checklist

## Troubleshooting

### Command not found after install

```bash
# Check Python scripts directory is in PATH
pip show conanx

# Try running with python -m
python -m conanx --help

# Reinstall
pip uninstall conanx
pip install conanx
```

### Changes not reflected

When developing:
```bash
# Reinstall in editable mode
pip install -e . --force-reinstall
```

### Import errors

Check:
- All `__init__.py` files exist
- Package is installed: `pip show conanx`
- No circular imports in the code
