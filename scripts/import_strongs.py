"""Align Strong's word tags to existing KJV tokens without changing scripture."""
from pathlib import Path
import difflib, hashlib, json, re
from lxml import etree
ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist';SRC=ROOT/'sources'
TOKEN=re.compile(r"[A-Za-z0-9]+(?:[’'][A-Za-z0-9]+)*")
def tokens(s):return [m[0] for m in TOKEN.finditer(s)]
def key(t):return t.lower().replace('’',"'")
def run():
 bible=json.loads((DIST/'bible.json').read_text());xml=etree.parse(str(SRC/'kjv-strongs/eng-kjv2006_usfx.xml'));books=xml.findall('book')
 assert len(books)==len(bible['books'])==66
 out=DIST/'strongs/tags';out.mkdir(parents=True,exist_ok=True);stats={'books':66,'chapters':0,'verses':0,'linkedTokens':0,'unmatchedSourceTaggedTokens':0,'sourceDifferences':[],'source':'https://ebible.org/find/show.php?id=eng-kjv2006','verseTextChanged':False}
 for bi,book in enumerate(books,1):
  source={};current={'c':0,'v':None}
  def add(text,ids=()):
   if current['v'] is not None:
    source.setdefault((current['c'],current['v']),[]).extend((t,list(ids)) for t in tokens(text or ''))
  def walk(node):
   tag=node.tag
   if tag in ('f','x','fig','h','toc','id'):return
   if tag=='c':current['c']=int(node.get('id'));current['v']=None;return
   if tag=='v':
    v=node.get('id','');current['v']=int(v) if v.isdigit() else None;return
   if tag=='ve':current['v']=None;return
   if tag=='w':
    ids=[]
    for prefix,n in re.findall(r'([HG])(\d+)',node.get('s','')):
     if 0<int(n)<=(8674 if prefix=='H' else 5624):ids.append(prefix+str(int(n)))
    add(''.join(node.itertext()),list(dict.fromkeys(ids)));return
   add(node.text)
   for child in node:walk(child);add(child.tail)
  walk(book);chapters={}
  for ci,verses in enumerate(bible['books'][bi-1]['chapters'],1):
   tagged={};stats['chapters']+=1
   for vi,text in enumerate(verses,1):
    original=tokens(text);src=source.get((ci,vi),[]);assert src,(bi,ci,vi)
    mapped=[[] for _ in original];matched=set()
    sm=difflib.SequenceMatcher(None,[key(t) for t,_ in src],[key(t) for t in original],autojunk=False)
    for block in sm.get_matching_blocks():
     for offset in range(block.size):
      i,j=block.a+offset,block.b+offset;mapped[j]=src[i][1];matched.add(i)
    if [key(t) for t,_ in src]!=[key(t) for t in original]:stats['sourceDifferences'].append([bi,ci,vi])
    stats['unmatchedSourceTaggedTokens']+=sum(bool(ids) for i,(_,ids) in enumerate(src) if i not in matched)
    stats['linkedTokens']+=sum(bool(ids) for ids in mapped);stats['verses']+=1
    tagged[str(vi)]={'w':[[t,ids] for t,ids in zip(original,mapped)]}
   chapters[str(ci)]=tagged
  (out/f'{bi}.json').write_text(json.dumps(chapters,ensure_ascii=False,separators=(',',':')))
 alllex={}
 for prefix,name in [('H','strongs-hebrew-dictionary.js'),('G','strongs-greek-dictionary.js')]:
  raw=(SRC/name).read_text();start=raw.index('{',raw.index('Dictionary ='));end=raw.rfind('}')+1;data=json.loads(raw[start:end]);alllex.update(data)
  sharddir=DIST/'strongs/lexicon'/prefix;sharddir.mkdir(parents=True,exist_ok=True);shards={}
  for ident,e in data.items():
   id=prefix+str(int(ident[1:]));record={'id':id,'lemma':e.get('lemma',''),'transliteration':e.get('xlit',e.get('translit','')),'pronunciation':e.get('pron',''),'definition':e.get('strongs_def','').strip(),'kjvRenderings':e.get('kjv_def',''),'derivation':e.get('derivation','')}
   shards.setdefault(int(id[1:])//1000,{})[id]=record
  for bucket,records in shards.items():(sharddir/f'{bucket}.json').write_text(json.dumps(records,ensure_ascii=False,separators=(',',':')))
 stats['lexiconEntries']=len(alllex);stats['dictionarySource']='https://github.com/openscriptures/strongs';stats['dictionaryLicense']='CC-BY-SA, as specified in the retained Open Scriptures source headers.';stats['sourceZipSha256']=hashlib.sha256((SRC/'kjv-strongs-usfx.zip').read_bytes()).hexdigest()
 (DIST/'strongs/manifest.json').write_text(json.dumps(stats,indent=2));print({k:v for k,v in stats.items() if not isinstance(v,list)})
if __name__=='__main__':run()
