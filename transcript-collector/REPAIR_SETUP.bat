@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\setup-complete-010" del ".venv\setup-complete-010"
call START_HERE.bat
