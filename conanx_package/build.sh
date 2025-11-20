#!/bin/bash
# Build script for ConanX package

set -e  # Exit on error

echo "========================================="
echo "Building ConanX Package"
echo "========================================="

# Clean old builds
echo "Cleaning old build artifacts..."
rm -rf build/ dist/ *.egg-info conanx.egg-info

# Build the package
echo "Building package..."
python -m build

# Check the package
echo "Checking package..."
twine check dist/*

echo ""
echo "========================================="
echo "Build complete!"
echo "========================================="
echo ""
echo "Distribution files created:"
ls -lh dist/
echo ""
echo "Next steps:"
echo "  - Test locally: pip install -e ."
echo "  - Upload to TestPyPI: twine upload --repository testpypi dist/*"
echo "  - Upload to PyPI: twine upload dist/*"
