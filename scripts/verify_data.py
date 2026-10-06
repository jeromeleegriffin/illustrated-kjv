from pathlib import Path
import hashlib,json,re,sqlite3
from lxml import html
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist';WORKSPACE=ROOT.parent
old=json.loads((ROOT/'sources/original-kjv.json').read_text());new=json.loads((DIST/'bible.json').read_text());assert len(old)==len(new['books'])==66
assert all(a['chapters']==b['chapters'] for a,b in zip(old,new['books']))
versecount=sum(len(c) for b in new['books'] for c in b['chapters']);assert versecount==31102
embedded=lambda path:json.loads(re.search(r'<script[^>]*id="embeddedBank"[^>]*>(.*?)</script>',path.read_text(),re.S)[1])
bankold=embedded(ROOT/'sources/original-trivia.html');banknew=embedded(DIST/'trivia.html');assert bankold==banknew;assert len(banknew['questions'])==5000
notes=[n for path in sorted((DIST/'bullinger/books').glob('*.json')) for n in json.loads(path.read_text())];assert len(notes)==23934
exceptions=[n for n in notes if 'referenceStatus' in n];assert len(exceptions)==12;assert sum(n['referenceStatus']=='unresolved' for n in exceptions)==8
idx=json.loads((DIST/'bullinger/appendix-index.json').read_text());assert idx['standardAppendices']==198 and idx['count']==200 and not idx['errors'];assert {str(i) for i in range(1,199)}<={e['id'] for e in idx['appendices']}
for e in idx['appendices']:
 path=DIST/'bullinger/appendices'/(e['id']+'.html');doc=html.parse(str(path));assert not doc.xpath('//script|//form|//iframe|//object|//embed')
 for node in doc.iter():assert not any(k.lower().startswith('on') for k in node.attrib)
 for src in doc.xpath('//img/@src'):assert (path.parent/src).resolve().is_file(),src
lex={}
for p in (DIST/'strongs/lexicon').rglob('*.json'):lex.update(json.loads(p.read_text()))
linked=0;chapters=0;missing=set()
for bi,book in enumerate(new['books'],1):
 tags=json.loads((DIST/'strongs/tags'/f'{bi}.json').read_text());assert len(tags)==len(book['chapters'])
 for ci,verses in enumerate(book['chapters'],1):
  chapter=tags[str(ci)];assert len(chapter)==len(verses);chapters+=1
  for vi,verse in enumerate(verses,1):
   words=chapter[str(vi)]['w'];assert [w[0] for w in words]==re.findall(r"[A-Za-z0-9]+(?:[’'][A-Za-z0-9]+)*",verse)
   for _,ids in words:
    linked+=bool(ids);missing.update(id for id in ids if id not in lex)
report={'status':'PASS','scripture':{'books':66,'chapters':chapters,'verses':versecount,'changedVerses':0,'originalSourceSha256':hashlib.sha256((ROOT/'sources/original-kjv.json').read_bytes()).hexdigest()},'trivia':{'questions':5000,'originalQuestionBankPreserved':True},'bullinger':{'notes':len(notes),'numberedAppendices':198,'supplements':2,'localImages':idx['imageCount'],'psalmTitleNotes':4,'unresolvedSourceVerseNumbers':8,'printedBookIntroductionsAndEveryDiagramCertified':False},'strongs':{'linkedWordTokens':linked,'dictionaryRecords':len(lex),'missingTaggedDictionaryIds':sorted(missing)}}
assert linked==361947 and len(lex)==14197 and not missing,report['strongs']
(ROOT/'verification').mkdir(exist_ok=True);(ROOT/'verification/data-integrity.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
