@echo off
REM Preflight checks for ELECTRE III project
REM Usage: scripts\run_preflight.bat [--run-tests] [--verbose]

echo Running preflight checks...
echo.

python "%~dp0preflight_checks.py" %*

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Preflight checks passed. Safe to commit.
) else (
    echo.
    echo Preflight checks failed. Fix issues before committing.
    exit /b 1
)
