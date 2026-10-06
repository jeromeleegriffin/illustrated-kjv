"""Import attributed public-domain Companion Bible notes and appendices."""
from pathlib import Path
import concurrent.futures, hashlib, html as html_std, json, re, sqlite3, urllib.request
from urllib.parse import urljoin, urlparse
from lxml import html, etree
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'sources'; DIST=ROOT/'dist'; BASE='https://www.levendwater.org'

def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'KJVStudyReader/1.0 (public-domain archival import)'})
    with urllib.request.urlopen(req,timeout=25) as r: return r.read()

def plain(fragment):
    el=html.fragment_fromstring(fragment,create_parent='div')
    for br in el.iter('br'): br.tail='\n'+(br.tail or '')
    for p in el.iter():
        if p.tag in ('p','div','h1','h2','h3','li'): p.tail='\n\n'+(p.tail or '')
    return el.text_content().strip()

def notes():
    bible=json.loads((DIST/'bible.json').read_text())
    c=sqlite3.connect(SRC/'module/SI-CBNOTES.commentaries.SQLite3')
    codes=[x[0] for x in c.execute('select distinct book_number from commentaries order by book_number')]
    assert len(codes)==len(bible['books'])==66
    target=DIST/'bullinger/books';target.mkdir(parents=True,exist_ok=True)
    total=0;invalid=[];chapters=set();counts={}
    for bi,code in enumerate(codes,1):
        book=bible['books'][bi-1]; records=[]
        for b,cf,vf,ct,vt,content in c.execute('select * from commentaries where book_number=? order by chapter_number_from,verse_number_from',(code,)):
            valid=1<=cf<=ct<=len(book['chapters']) and 1<=vf<=len(book['chapters'][cf-1]) and 1<=vt<=len(book['chapters'][ct-1])
            record={'c':cf,'v':vf,'tc':ct,'tv':vt,'text':plain(content)}
            if not valid:
                status='title' if vf==vt==0 else 'unresolved'
                record['referenceStatus']=status
                invalid.append({'book':bi,'c':cf,'v':vf,'tc':ct,'tv':vt,'status':status})
            records.append(record)
            for ch in range(cf,ct+1):chapters.add((bi,ch))
        (target/f'{bi}.json').write_text(json.dumps(records,ensure_ascii=False,separators=(',',':')))
        total+=len(records);counts[book['name']]=len(records)
    assert all(1<=x['c']<=len(bible['books'][x['book']-1]['chapters']) for x in invalid)
    assert total==23934,total
    manifest={'title':'The Companion Bible Notes','editor':'E. W. Bullinger','entries':total,'books':66,'chaptersWithNotes':len(chapters),'bookCounts':counts,'source':'https://www.sermonindex.net/modules/','moduleUrl':'https://www.sermonindex.net/modules/mybible/SI-CBNOTES.commentaries.zip','sourceSha256':hashlib.sha256((SRC/'bullinger-notes.zip').read_bytes()).hexdigest(),'rights':'Original work: public domain. Module provider explicitly states free to copy and pass on.','referenceExceptions':invalid,'sourceInfo':dict(c.execute('select * from info')),'limitations':'All records in the named module are imported. Printed book introductions and every original structural diagram are not certified against scans.'}
    (DIST/'bullinger/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print('Notes imported:',total,'in',len(chapters),'chapters',flush=True)

ALLOWED={'div','p','br','span','b','strong','i','em','u','h1','h2','h3','h4','h5','h6','ul','ol','li','table','thead','tbody','tr','td','th','blockquote','pre','sup','sub','hr','a','img','center'}

def appendices():
    index=html.parse(str(SRC/'appendix-index.html')); entries={}
    for a in index.xpath('//a[@href]'):
        m=re.search(r'/companion/append(\d+[a-z]?)(?:\.html)(?:#.*)?$',a.get('href'),re.I)
        if m:
            num=m[1].upper()
            if num not in entries: entries[num]={'id':num,'title':' '.join(a.text_content().split()),'source':urljoin(BASE,a.get('href').split('#')[0])}
    assert all(str(n) in entries for n in range(1,199))
    # The index also links the detailed chronological table under Appendix 50.
    entries['50_VIII']={'id':'50_VIII','title':'Appendix 50 — Chronological tables, section VIII','source':BASE+'/companion/append50_VIII.html'}
    dest=DIST/'bullinger/appendices'; dest.mkdir(parents=True,exist_ok=True)
    rawdir=SRC/'appendix-pages';rawdir.mkdir(parents=True,exist_ok=True)
    errors=[];images={}
    def download(entry):
        f=rawdir/(entry['id']+'.html')
        data=f.read_bytes() if f.exists() else get(entry['source'])
        if not f.exists(): f.write_bytes(data)
        doc=html.fromstring(data,base_url=entry['source']);body=doc.find('body')
        if body is None: raise ValueError('No body: '+entry['id'])
        for el in list(body.xpath('.//script|.//style|.//form|.//iframe|.//object|.//embed|.//input|.//button')): el.drop_tree()
        # Remove the source website's navigation/footer; preserve Bullinger's content.
        for a in list(body.xpath('.//a[@href]')):
            if 'index_companion' in a.get('href','') or 'voettekst' in ' '.join(a.xpath('.//@class')):
                parent=a.getparent()
                if parent is not None and parent.tag=='center': parent.drop_tree()
        for el in list(body.xpath('.//*[contains(@class,"voettekst")]')):
            if el.getparent() is not None: el.drop_tree()
        for el in list(body.iterdescendants()):
            if not isinstance(el.tag,str):
                if el.getparent() is not None: el.getparent().remove(el)
                continue
            if el.tag not in ALLOWED:
                el.drop_tag();continue
            old=dict(el.attrib);el.attrib.clear()
            for k in ('colspan','rowspan'):
                if old.get(k,'').isdigit():el.set(k,old[k])
            anchor=old.get('id') or old.get('name')
            if anchor and re.fullmatch(r'[\w.-]+',anchor): el.set('id',anchor)
            if el.tag=='a':
                href=urljoin(entry['source'],old.get('href',''))
                m=re.search(r'/companion/append(\d+[a-z]?|50_VIII)\.html(?:#(.*))?$',href,re.I)
                if m:
                    num=m[1].upper(); frag=('#'+m[2]) if m[2] else ''
                    el.set('href','../../appendices.html?n='+num+frag);el.set('target','_parent')
                elif urlparse(href).scheme in ('https','http'):
                    el.set('href',href);el.set('target','_blank');el.set('rel','noopener')
            if el.tag=='img':
                url=urljoin(entry['source'],old.get('src',''))
                if urlparse(url).hostname and urlparse(url).hostname.endswith('levendwater.org'):
                    ext=Path(urlparse(url).path).suffix.lower()
                    if ext not in ('.png','.jpg','.jpeg','.gif','.svg'):ext='.img'
                    name=hashlib.sha256(url.encode()).hexdigest()[:24]+ext
                    images[url]=name
                    el.set('src','../images/'+name);el.set('alt',old.get('alt','Original Companion Bible diagram'));el.set('loading','lazy')
                else:el.drop_tree()
        text=body.text_content()
        if len(text.strip())<150 and not body.xpath('.//img'):raise ValueError('Suspiciously short appendix: '+entry['id'])
        fragment=''.join(html.tostring(el,encoding='unicode') for el in body)
        page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Companion Bible Appendix '+entry['id']+'</title><link rel="stylesheet" href="../../appendix-content.css"><body class="bullinger-appendix">'+fragment+'</body></html>'
        (dest/(entry['id']+'.html')).write_text(page)
        return entry
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures={pool.submit(download,e):e for e in entries.values()}
        success=[]
        for fut in concurrent.futures.as_completed(futures):
            e=futures[fut]
            try:success.append(fut.result())
            except Exception as err: errors.append({'id':e['id'],'source':e['source'],'error':str(err)});print('Appendix error',e['id'],str(err),flush=True)
    idir=DIST/'bullinger/images';idir.mkdir(parents=True,exist_ok=True)
    def image(item):
        url,name=item; f=idir/name
        if not f.exists():f.write_bytes(get(url))
        return name
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for fut in concurrent.futures.as_completed([pool.submit(image,i) for i in images.items()]):
            try:fut.result()
            except Exception as e:errors.append({'imageError':str(e)})
    success.sort(key=lambda e:(int(re.match(r'\d+',e['id'])[0]),e['id']))
    manifest={'appendices':success,'count':len(success),'standardAppendices':sum(e['id'].isdigit() for e in success),'imageCount':len(images),'errors':errors,'sourceIndex':BASE+'/companion/index_companion.html','rights':'Original Companion Bible appendices by E. W. Bullinger; public-domain original text. Adapted presentation, original source linked.'}
    (DIST/'bullinger/appendix-index.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print('Appendices imported:',len(success),'images:',len(images),'errors:',len(errors),flush=True)
    if errors:raise RuntimeError('Incomplete import: see appendix-index.json')

if __name__=='__main__':
    notes();appendices()
