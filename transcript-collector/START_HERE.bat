@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\setup-complete-009" if exist ".venv\Scripts\python.exe" goto run
if exist ".venv\Scripts\python.exe" goto dependencies
py -3.12 --version >nul 2>&1
if errorlevel 1 (
 echo Install free Python 3.12 for Windows from python.org with Tcl/Tk enabled.
 echo Then double-click START_HERE.bat again. No Python programming is needed.
 start https://www.python.org/downloads/windows/
 pause
 exit /b 1
)
py -3.12 -m venv .venv
if errorlevel 1 goto fail
:dependencies
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto fail
echo installed> .venv\setup-complete-009
:run
.venv\Scripts\python.exe app.py
if errorlevel 1 goto fail
exit /b 0
:fail
echo Setup or launch failed. Read the error above. No collection was marked complete.
pause
exit /b 1
