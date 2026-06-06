@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

set "PROJECT_ROOT=%CD%"
set "SCANNER=%PROJECT_ROOT%\..\..\_tools\build_exclude_scanner.py"
set "BUILD_ROOT=C:\_Local_DEV\codex_build\methodenanalyser"
set "DIST_DIR=%PROJECT_ROOT%\dist"

if not exist "%SCANNER%" (
    echo [FEHLER] Build-Exclude-Scanner nicht gefunden:
    echo %SCANNER%
    exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python wurde nicht gefunden.
    exit /b 1
)

for /f "delims=" %%E in ('python "%SCANNER%" --project "%PROJECT_ROOT%" --emit pyinstaller') do set "EXCLUDES=%%E"

if not exist "%BUILD_ROOT%" mkdir "%BUILD_ROOT%"
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

python -m PyInstaller --noconfirm --clean --windowed --onefile ^
  --name MethodenAnalyser ^
  --icon "%PROJECT_ROOT%\MethodenAnalyser.ico" ^
  %EXCLUDES% ^
  --distpath "%BUILD_ROOT%\dist" ^
  --workpath "%BUILD_ROOT%\build" ^
  --specpath "%BUILD_ROOT%" ^
  "%PROJECT_ROOT%\MethodenAnalyser3.py"

if errorlevel 1 (
    echo [FEHLER] PyInstaller-Build fehlgeschlagen.
    exit /b 1
)

copy /Y "%BUILD_ROOT%\dist\MethodenAnalyser.exe" "%DIST_DIR%\MethodenAnalyser.exe" >nul
copy /Y "%BUILD_ROOT%\dist\MethodenAnalyser.exe" "%PROJECT_ROOT%\MethodenAnalyser.exe" >nul

echo [OK] EXE gebaut:
echo %DIST_DIR%\MethodenAnalyser.exe
endlocal
