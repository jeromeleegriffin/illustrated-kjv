"""Run on Windows after tests; package and execute the frozen application."""
import hashlib,json,os,shutil,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
 if os.name!='nt':raise SystemExit('Windows packaging must run on Windows')
 out=ROOT/'build-output';out.mkdir(exist_ok=True)
 subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onedir','--name','GriffinFAQProcessor','--distpath',str(out),'--workpath',str(ROOT/'build-cache'),'--specpath',str(ROOT/'build-cache'),str(ROOT/'app.py')],check=True,cwd=ROOT)
 exe=out/'GriffinFAQProcessor'/'GriffinFAQProcessor.exe'
 subprocess.run([str(exe),'--self-test'],check=True,timeout=60)
 subprocess.run([sys.executable,str(ROOT/'tests'/'frozen_smoke.py'),str(exe)],check=True,timeout=90)
 landing=out/'GriffinFAQProcessor'/'index.html'
 landing.write_text('<!doctype html><meta charset="utf-8"><title>Start Griffin FAQ Processor</title><h1>Griffin Shepherd’s Chapel FAQ Batch Processor</h1><p>Extract this entire ZIP first. Double-click START_HERE.bat or GriffinFAQProcessor.exe. Keep the program window open.</p><p>Import your private teaching library ZIP. Click Set up free AI (one-time downloads), then Start. No Python installation is needed.</p><p>Windows 10 22H2 or later, 64-bit; 16 GB RAM recommended and 14 GB free disk space. Keep Windows awake while processing. Results are private AI candidates requiring review before public publication.</p><p>Read README.txt and TEST_REPORT.md for current validation and limits.</p>',encoding='utf-8')
 (landing.parent/'START_HERE.bat').write_text('@echo off\r\ncd /d "%~dp0"\r\nGriffinFAQProcessor.exe\r\nif errorlevel 1 pause\r\n')
 for name in ('README.txt','TEST_REPORT.md'):
  if (ROOT/name).exists():shutil.copyfile(ROOT/name,landing.parent/name)
 for src in ROOT.glob('*.py'):shutil.copyfile(src,landing.parent/('source-'+src.name))
 zip_path=out/'Griffin_FAQ_Processor_Windows_001.zip'
 with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(landing.parent.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(landing.parent))
 with zipfile.ZipFile(zip_path) as z:
  assert 'index.html' in z.namelist() and 'START_HERE.bat' in z.namelist() and 'GriffinFAQProcessor.exe' in z.namelist()
  assert z.testzip() is None
 print(json.dumps({'package':str(zip_path),'bytes':zip_path.stat().st_size,'sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),'windows_frozen_self_test':'passed'}))

if __name__=='__main__':main()
