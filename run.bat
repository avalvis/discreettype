@echo off
setlocal enabledelayedexpansion

:: Discreet Typing Tool - Smart Launcher
:: This script ensures the environment is ready and launches the app.

title Discreet Typing Tool Launcher

:: 1. Check for 'uv' (the modern Python package manager)
where uv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] 'uv' is not installed. 
    echo Please install it from https://github.com/astral-sh/uv or run:
    echo powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    pause
    exit /b 1
)

:: 2. Sync dependencies silently if needed
:: 'uv sync' is fast and ensures the virtual environment matches pyproject.toml
echo [BOOT] Preparing environment...
uv sync --quiet
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to sync dependencies. Checking internet connection...
    pause
    exit /b 1
)

:: 3. Launch the application
:: We use 'uv run' to automatically use the correct virtual environment
echo [BOOT] Launching Discreet Typing Tool...
uv run python -m typing_tool.main

if %ERRORLEVEL% neq 0 (
    if %ERRORLEVEL% neq 1 (
        :: Don't pause on clean exit (Ctrl+C usually returns 1 or 0)
        echo.
        echo [INFO] Application closed with code %ERRORLEVEL%.
        pause
    )
)

endlocal
