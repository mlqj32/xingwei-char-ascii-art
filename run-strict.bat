@echo off
setlocal
cd /d "%~dp0"
set CHARART_STRICT=1
if exist ".venv\Scripts\python.exe" (
  .venv\Scripts\python.exe run.py
) else (
  py -3.13 run.py
)
