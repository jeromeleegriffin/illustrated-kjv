"""Windows CI: Edge UI against the packaged executable, synthetic captions only."""
import json,subprocess,sys,tempfile,time,zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
 exe=Path(sys.argv[1]).resolve()
 with tempfile.TemporaryDirectory() as tmp:
  root=Path(tmp);proc=subprocess.Popen([str(exe),'--data',str(root),'--no-browser'])
  try:
   for _ in range(150):
    if (root/'session.json').exists():break
    time.sleep(.1)
   url=json.loads((root/'session.json').read_text())['url']
   fixture=root/'fixture.zip'
   with zipfile.ZipFile(fixture,'w') as z:z.writestr('search-library/transcripts/abcdefghijk.json',json.dumps({'id':'abcdefghijk','teacher':'Arnold Murray','duration':20,'segments':[{'start':0,'end':20,'text':'Synthetic UI test.'}]}))
   with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True);page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(url);page.wait_for_function("document.querySelector('#counts').textContent.includes('Recordings imported: 0')")
    page.locator('#file').set_input_files(str(fixture));page.locator('#import').click()
    page.wait_for_function("document.querySelector('#counts').textContent.includes('Recordings imported: 1')")
    page.reload();page.wait_for_function("document.querySelector('#counts').textContent.includes('Recordings imported: 1')")
    page.locator('#pause').click();page.wait_for_function("document.querySelector('#message').textContent.includes('Pausing')")
    with page.expect_download() as download:page.locator('#export').click()
    download.value.save_as(str(root/'result.zip'))
    with zipfile.ZipFile(root/'result.zip') as z:assert z.testzip() is None
    assert not errors,errors
    page.screenshot(path=str(exe.parent/'UI-test.png'),full_page=True)
    browser.close();print('Frozen Windows Edge UI: startup, import, refresh/session resume, pause, export and JavaScript checks passed')
  finally:proc.terminate();proc.wait(timeout=15)

if __name__=='__main__':main()
