@echo off
SETLOCAL
cd /d "%~dp0"

where py >nul 2>&1 && set "PY=py -3.13" || set "PY=python"

if not exist ".venv" (
  echo Creating venv...
  %PY% -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -r requirements.txt -q
python run.py
ENDLOCAL
