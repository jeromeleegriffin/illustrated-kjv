"""Windows CI: Edge UI against the packaged executable, synthetic captions only."""
import json,subprocess,sys,tempfile,time,zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from publication import render_preview

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
    page.locator('#hardware').select_option('cpu');page.locator('#settings').click()
    page.wait_for_function("document.querySelector('#message').textContent.includes('Import finished') || document.querySelector('#hardware').value==='cpu'")
    page.wait_for_timeout(3000)
    page.reload();page.wait_for_function("document.querySelector('#counts').textContent.includes('Recordings imported: 1')")
    page.wait_for_function("document.querySelector('#hardware').value==='cpu'");page.wait_for_function("document.querySelector('#runtime').textContent.includes('Current section elapsed')")
    page.locator('#pause').click();page.wait_for_function("document.querySelector('#message').textContent.includes('Pausing')")
    with page.expect_download() as download:page.locator('#export').click()
    download.value.save_as(str(root/'result.zip'))
    with zipfile.ZipFile(root/'result.zip') as z:
     assert z.testzip() is None
     assert 'publication/preflight.json' in z.namelist()
     assert 'publication/faq-preview.html' in z.namelist()
     preview=root/'preview.html';preview.write_bytes(z.read('publication/faq-preview.html'))
    page.goto(preview.as_uri());page.wait_for_function("document.querySelector('.position').textContent==='0 / 0'")
    assert page.locator('main').inner_text().find('No proposals passed')>=0
    synthetic={'proposals':[{'question':'Synthetic question '+str(i)+'?','summary':'Synthetic preview test only.','teacher':'Arnold Murray','video_id':'abcdefghijk','start':10,'source_url':'https://www.youtube.com/watch?v=abcdefghijk&t=10s','grouping_basis':'test_only'} for i in range(3)]}
    preview.write_text(render_preview(synthetic,{}),encoding='utf-8');page.reload()
    page.wait_for_function("document.querySelector('.position').textContent==='1 / 3'")
    positions=[page.locator('header .next').bounding_box(),page.locator('footer .next').bounding_box()]
    page.locator('header .next').click();assert page.locator('article:not([hidden]) h2').inner_text()=='Synthetic question 1?'
    page.locator('footer .next').click();assert page.locator('article:not([hidden]) h2').inner_text()=='Synthetic question 2?'
    assert page.locator('header .next').bounding_box()['y']==positions[0]['y'];assert page.locator('footer .next').bounding_box()['y']==positions[1]['y']
    page.locator('footer .prev').click();assert page.locator('article:not([hidden]) h2').inner_text()=='Synthetic question 1?'
    assert not errors,errors
    page.screenshot(path=str(exe.parent/'UI-test.png'),full_page=True)
    browser.close();print('Frozen Windows Edge UI: startup, import, refresh/session resume, pause, export and JavaScript checks passed')
  finally:proc.terminate();proc.wait(timeout=15)

if __name__=='__main__':main()


