@echo off
echo ===================================
echo Testing PDF Chunking System Environment
echo ===================================

REM Check if .env file exists, if not copy the fallback version
if not exist "config\.env" (
    echo Config file not found, using fallback configuration...
    copy config\.env.fallback config\.env
)

poetry run test-env
echo.
echo.
echo ===================================
echo Press any key to continue to system startup...
echo Press Ctrl+C to exit if you need to make changes
echo ===================================
pause > nul
echo Starting PDF Chunking System...
poetry run start
