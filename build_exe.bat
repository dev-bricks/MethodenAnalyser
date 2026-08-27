@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

set "PROJECT_ROOT=%CD%"
set "SCANNER=%PROJECT_ROOT%\..\..\_tools\build_exclude_scanner.py"
set "BUILD_ROOT=C:\_Local_DEV\codex_build\methodenanalyser"
set "DIST_DIR=%PROJECT_ROOT%\dist"

rem Toolchain contract: install requirements-dev.txt and read BUILD.md first.
rem Verified PyInstaller range: >=6.14.2,<7.0.
python -c "import PyInstaller; print('[INFO] PyInstaller ' + PyInstaller.__version__)" >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] PyInstaller fehlt. Installiere requirements-dev.txt.
    exit /b 1
)

set "EXCLUDES="
if exist "%SCANNER%" (
    for /f "delims=" %%E in ('python "%SCANNER%" --project "%PROJECT_ROOT%" --emit pyinstaller') do set "EXCLUDES=%%E"
) else (
    echo [HINWEIS] Build-Exclude-Scanner nicht vorhanden, fahre ohne dynamische Excludes fort.
)

if not exist "%BUILD_ROOT%" mkdir "%BUILD_ROOT%"
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

python -m PyInstaller --noconfirm --clean --windowed --onefile ^
  --name MethodenAnalyser ^
  --icon "%PROJECT_ROOT%\MethodenAnalyser.ico" ^
  --add-data "%PROJECT_ROOT%\locales;locales" ^
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
