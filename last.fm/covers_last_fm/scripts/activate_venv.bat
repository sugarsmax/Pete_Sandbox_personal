@echo off
REM Activates the appropriate Python virtual environment for this project (Windows)
REM Priority order:
REM  1. %USERPROFILE%\python\venv (local machine override)
REM  2. COVERS_VENV environment variable (if set)
REM  3. Creates a local venv if none exist

setlocal enabledelayedexpansion

REM Get project directory (parent of scripts folder)
for %%I in ("%~dp0..") do set "PROJECT_DIR=%%~fI"

set "LOCAL_VENV=%USERPROFILE%\python\venv"

REM Check custom venv from environment variable
if defined COVERS_VENV (
    if exist "%COVERS_VENV%\Scripts\activate.bat" (
        echo [covers_last_fm] Activating custom venv at: %COVERS_VENV%
        call "%COVERS_VENV%\Scripts\activate.bat"
        goto show_version
    )
)

REM Check local venv
if exist "%LOCAL_VENV%\Scripts\activate.bat" (
    echo [covers_last_fm] Activating local override at: %LOCAL_VENV%
    call "%LOCAL_VENV%\Scripts\activate.bat"
    goto show_version
)

REM No venv found - offer to create one
echo.
echo [covers_last_fm] No Python virtual environment found.
echo.
echo Available options:
echo   1. Use local venv at: %LOCAL_VENV% (requires setup)
echo   2. Set COVERS_VENV environment variable
echo   3. Create a new venv in this project
echo.

set /p CREATE_VENV="Create new venv in project directory? (y/n): "
if /i "%CREATE_VENV%"=="y" (
    if not exist "%PROJECT_DIR%\.venv" (
        echo [covers_last_fm] Creating venv at: %PROJECT_DIR%\.venv
        python -m venv "%PROJECT_DIR%\.venv"
    )
    call "%PROJECT_DIR%\.venv\Scripts\activate.bat"
    echo [covers_last_fm] Installing requirements...
    python -m pip install --upgrade pip
    python -m pip install requests beautifulsoup4 pyyaml playwright
    echo [covers_last_fm] Installing Playwright browser...
    python -m playwright install chromium
    echo [covers_last_fm] Setup complete!
) else (
    echo [covers_last_fm] Activation skipped. Please set up a venv manually.
    exit /b 1
)

:show_version
echo [covers_last_fm] Python: 
python --version

