@echo off
SETLOCAL
cd /d "%~dp0"

where py >nul 2>&1 && set "PY=py -3.13" || set "PY=python"

if not exist ".venv" (
  echo Creating venv...
  %PY% -m venv .venv
)
call .venv\Scripts\activate.bat

pip install -r requirements-build.txt -q
python tools\verify_native.py
if errorlevel 1 (
  echo [ERROR] verify_native failed
  pause & exit /b 1
)

python tools\parity_check.py
if errorlevel 1 (
  echo [WARN] parity_check failed
)

echo.
echo Building exe with PyInstaller...
pyinstaller charart.spec --noconfirm
if errorlevel 1 (
  echo [ERROR] PyInstaller failed
  pause & exit /b 1
)

echo.
echo Done: dist\星薇字符画.exe
ENDLOCAL
