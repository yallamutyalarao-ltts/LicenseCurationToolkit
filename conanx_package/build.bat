@echo off
REM Build script for ConanX package

echo =========================================
echo Building ConanX Package
echo =========================================

REM Clean old builds
echo Cleaning old build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist conanx.egg-info rmdir /s /q conanx.egg-info

REM Build the package
echo Building package...
python -m build

REM Check the package
echo Checking package...
twine check dist/*

echo.
echo =========================================
echo Build complete!
echo =========================================
echo.
echo Distribution files created:
dir dist
echo.
echo Next steps:
echo   - Test locally: pip install -e .
echo   - Upload to TestPyPI: twine upload --repository testpypi dist/*
echo   - Upload to PyPI: twine upload dist/*

pause
