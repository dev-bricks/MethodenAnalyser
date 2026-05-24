@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8

py -3 webapp\server.py
if errorlevel 1 (
    python webapp\server.py
)
if errorlevel 1 pause
