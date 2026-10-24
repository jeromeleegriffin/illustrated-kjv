@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Please complete START_HERE.bat setup first, then close the collector.
 pause
 exit /b 1
)
echo Close the collector before testing. Do not run during an active cooldown.
echo Checks up to three known recordings and stops at the first failure.
echo Leaves your teaching library unchanged. No audio is downloaded.
echo Private captions and shareable report.json go into diagnostics.
echo Press Ctrl+C to cancel or any key to begin.
pause >nul
.venv\Scripts\python.exe diagnostic_captions.py --count 3
pause
