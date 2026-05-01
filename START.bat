@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

where py >nul 2>&1
if %ERRORLEVEL%==0 (
    py -3 "MethodenAnalyser3.py"
) else (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [FEHLER] Python wurde nicht gefunden.
        pause
        exit /b 1
    )
    python "MethodenAnalyser3.py"
)

if errorlevel 1 pause
