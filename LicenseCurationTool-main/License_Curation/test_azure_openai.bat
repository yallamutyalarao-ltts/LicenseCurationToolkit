@echo off
REM Test Azure OpenAI Configuration on Windows

echo ========================================
echo AZURE OPENAI CONFIGURATION TEST
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.11 or later
    exit /b 1
)

REM Run the test script
python test_azure_openai.py

exit /b %errorlevel%
