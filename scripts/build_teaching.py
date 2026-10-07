"""Build conservative Bible-wide range mapping from cached public source evidence."""
import json,re,pathlib,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
CACHE=ROOT/'sources/teaching'
bible=json.loads((ROOT/'dist/bible.json').read_text())
names=[b['name'] for b in bible['books']]
aliases={n.lower():i for i,n in enumerate(names)}
aliases.update({'psalm':18,'song of songs':21})
for i,n in enumerate(names):
    if n[0] in '123':
        number,word=n.split(' ',1)
        for prefix in [dict(zip('123',['I','II','III']))[number],number+{'1':'st','2':'nd','3':'rd'}[number]]:
            aliases[(prefix+' '+word).lower()]=i
            aliases[(prefix+' Epistle of '+word).lower()]=i
aliases['timothy']=53
bookPattern='|'.join(re.escape(x).replace(r'\ ',r'\s+') for x in sorted(aliases,key=len,reverse=True))
pattern=re.compile(r'(?<![A-Za-z])('+bookPattern+r')\s*(?:Chapter|[~:-])?\s+(\d+)[:.\s]+(\d+)\s*(?:[-–—]|\bto\b|\s)\s*(?:(\d+)[:.\s]+(\d+)|(END))',re.I)
namedBook=re.compile(r'(?<![A-Za-z])('+bookPattern+r')(?![A-Za-z])',re.I)
def valid(b,p):
    c,v=p;return 1<=c<=len(bible['books'][b]['chapters']) and 1<=v<=len(bible['books'][b]['chapters'][c-1])
def parse_all(title):
    # Official Gospel of John titles can begin with a four-digit lecture code.
    # Strip that code for parsing only; otherwise its last digit can look like an epistle number.
    title=re.sub(r"^\s*\d{4}\s+(?=John\b)","",title,flags=re.I)
    if re.search(r'\b(?:I|1st|2nd)\s*(?:&|and)\s*(?:II|III|2nd|3rd)\b',title,re.I):return []
    result=[]
    for m in pattern.finditer(title):
        b=aliases[re.sub(r'\s+',' ',m[1].lower())];start=[int(m[2]),int(m[3])]
        end=[int(m[4]),int(m[5])] if m[4] else [len(bible['books'][b]['chapters']),len(bible['books'][b]['chapters'][-1])]
        if valid(b,start) and valid(b,end) and start<=end:result.append((b,start,end))
    return result
def parse(title):
    result=parse_all(title);return result[0] if result else None
def build():
    lessons={};excluded=[];books=[{'name':n,'playlists':[],'lessons':[],'bookStudies':[]} for n in names]
    # Preserve every previously approved Genesis link, including its dated evidence.
    baseline=json.loads((ROOT/'dist/genesis-teaching.json').read_text())
    evidence={x['id']:x for x in json.loads((ROOT/'verification/genesis-video-sources.json').read_text())}
    for old in baseline['lessons']:
        ev=evidence.get(old['id'],{})
        if ev.get('status')=='OK' and ev.get('arnoldDescription'):
            l={**old,'book':0,'teacher':'Arnold Murray','channel':ev['author'],'official':True,'playlist':baseline['playlist'],'checked':baseline['checked'],'mappingBasis':'Previously verified published passage range'}
            lessons[(l['id'],0,tuple(l['start']),tuple(l['end']))]=l
    books[0]['playlists'].append(baseline['playlist'])
    catalogs=json.loads((CACHE/'catalog.json').read_text())
    extra=CACHE/'student-catalog.json'
    if extra.exists():catalogs+=json.loads(extra.read_text())
    extra=CACHE/'extra-catalog.json'
    if extra.exists():catalogs+=json.loads(extra.read_text())
    search=CACHE/'gap-search.json'
    if search.exists():catalogs.append({'url':None,'videos':{v['id']:v['title'] for vs in json.loads(search.read_text()).values() for v in vs}})
    for pl in catalogs:
        for vid,listedTitle in pl['videos'].items():
            file=CACHE/('video-'+vid+'.json')
            if not file.exists():excluded.append({'id':vid,'title':listedTitle,'reason':'Evidence not collected'});continue
            ev=json.loads(file.read_text());title=ev.get('title') or listedTitle
            desc=ev.get('description','');teacherText=title+'\n'+desc[:600]
            # A single named teacher is required; mixed recordings need passage-level evidence.
            teachers=[t for t in ['Arnold Murray','Dennis Murray'] if re.search(re.escape(t),teacherText,re.I)]
            if len(teachers)!=1:
                excluded.append({'id':vid,'title':title,'reason':'Single Arnold/Dennis teacher attribution not confirmed'});continue
            teacher=teachers[0]
            if ev.get('playability')!='OK':
                excluded.append({'id':vid,'title':title,'reason':'Video availability not confirmed'});continue
            parsed=parse_all(title)
            if not parsed:
                # Descriptions can state the range when the title only names the book.
                parsed=parse_all(desc[:600])
            if not parsed:
                # A clearly named book recording is useful without asserting verse coverage.
                bm=namedBook.search(title)
                if bm and not re.search(r'\d+[:.]\d+',title):
                    b=aliases[re.sub(r'\s+',' ',bm[1].lower())]
                    if not any(x['id']==vid for x in books[b]['bookStudies']):books[b]['bookStudies'].append({'id':vid,'title':title,'url':'https://www.youtube.com/watch?v='+vid,'channel':ev.get('author'),'teacher':teacher,'checked':ev.get('checked')})
                    if pl['url'] and pl['url'] not in books[b]['playlists']:books[b]['playlists'].append(pl['url'])
                excluded.append({'id':vid,'title':title,'reason':'Unambiguous valid passage range not published'});continue
            official=ev.get('channelId')=='UCwX0AEx-qIhQ9kgtlNhyIXw'
            for b,start,end in parsed:
                lesson={'id':vid,'title':title,'book':b,'start':start,'end':end,'url':'https://www.youtube.com/watch?v='+vid,'teacher':teacher,'channel':ev.get('author'),'official':official,'playlist':pl['url'],'timestampSeconds':None,'checked':ev.get('checked'),'mappingBasis':'Published passage range'}
                lessons[(vid,b,tuple(start),tuple(end))]=lesson
                if pl['url'] and pl['url'] not in books[b]['playlists']:books[b]['playlists'].append(pl['url'])
    for l in lessons.values():books[l['book']]['lessons'].append(l)
    coverage=[];gaps=[]
    for b,book in enumerate(books):
        book['lessons'].sort(key=lambda l:(l['teacher']!='Arnold Murray',not l['official'],l['start'],l['end'],l['id']))
        matched=0;missing=[]
        for c,verses in enumerate(bible['books'][b]['chapters'],1):
            for v in range(1,len(verses)+1):
                if any(l['start']<=[c,v]<=l['end'] for l in book['lessons']):matched+=1
                else:missing.append([c,v])
        total=sum(len(c) for c in bible['books'][b]['chapters'])
        book['coverage']={'matched':matched,'total':total}
        coverage.append({'book':book['name'],'lessons':len(book['lessons']),'matched':matched,'total':total})
        gaps.append({'book':book['name'],'verses':missing})
    output={'revision':'008','source':'https://shepherdschapel.com/video','checked':'2026-10-07','teacherPolicy':'Arnold Murray first; Dennis Murray fallback per verse.','mappingBasis':'Published chapter/verse ranges only; no audio timestamp synchronization. A single named Arnold/Dennis teacher attribution is required.','books':books}
    (ROOT/'dist/bible-teaching.json').write_text(json.dumps(output,ensure_ascii=False,separators=(',',':')))
    report={'status':'PARTIAL — more video verification required','coverage':coverage,'totalLessons':len(lessons),'totalMatched':sum(x['matched'] for x in coverage),'totalVerses':31102,'excluded':excluded,'gaps':gaps,'blocker':'YouTube HTTP 429 halted source collection. No blocked request was retried. Existing Genesis verification is retained. Teacher attribution is based on publisher metadata, not listening to every recording.'}
    (ROOT/'verification/bible-teaching-coverage.json').write_text(json.dumps(report,indent=2))
    print('Lessons',len(lessons),'matched',report['totalMatched'])
    for x in coverage:print(x['book'],x['lessons'],str(x['matched'])+'/'+str(x['total']))
if __name__=='__main__':build()
