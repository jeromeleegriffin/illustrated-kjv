"""Recalculate catalog coverage and reconcile only published official download links."""
import argparse,json,re,hashlib,urllib.request
from pathlib import Path
from collections import Counter
from engine import atomic,now
from prepare_queue import prepare

def catalog_audit(catalog,bible):
 data=json.loads(Path(catalog).read_text());kjv=json.loads(Path(bible).read_text());rows=prepare(catalog)
 covered=set();total=set();errors=[];exceptions=[]
 for bi,b in enumerate(kjv['books']):
  for ci,c in enumerate(b['chapters'],1):
   for vi,_ in enumerate(c,1):total.add((b['name'],ci,vi))
 for b in data['books']:
  for l in b['lessons']:
   try:
    lo=tuple(l['start']);hi=tuple(l['end'])
    if (b['name'],*lo) not in total or (b['name'],*hi) not in total or lo>hi:raise ValueError('Invalid passage bounds')
    covered.update(x for x in total if x[0]==b['name'] and lo<=x[1:]<=hi)
    if 'infer' in str(l).lower():exceptions.append({'id':l['id'],'teacher':l['teacher'],'basis':l.get('mappingBasis')})
   except Exception as e:errors.append({'id':l.get('id'),'error':str(e)})
 return {'checked':now(),'catalog_sha256':hashlib.sha256(Path(catalog).read_bytes()).hexdigest(),'books':len(data['books']),'mappings':sum(len(b['lessons']) for b in data['books']),'unique_recordings':len(rows),'teacher_counts':dict(Counter(r['teacher'] for r in rows)),'reused_mapping_count':sum(len(b['lessons']) for b in data['books'])-len(rows),'kjv_verses':len(total),'mapped_verses':len(covered),'missing_verses':sorted(total-covered),'mapping_errors':errors,'teacher_inference_records':exceptions,'note':'Catalog range coverage only. Does not prove recorded teaching covers every verse or verify inferred teacher identities.'}

def official_sources(catalog,page_html=None):
 from bs4 import BeautifulSoup
 url='https://shepherdschapel.com/audio'
 raw=page_html if page_html is not None else urllib.request.urlopen(url,timeout=30).read().decode()
 soup=BeautifulSoup(raw,'html.parser');links=[];seen=set()
 for a in soup.select('a[href]'):
  href=a['href']
  if not re.search(r'\.mp3(?:\?|$)',href,re.I) or href in seen:continue
  seen.add(href);context=a.parent.parent.get_text(' ',strip=True)
  links.append({'url':href,'published_context':context,'page':url,'access':'listed_not_download_verified'})
 rows=prepare(catalog);blocked={'2F0K2ip_82U','J2Ia_1jDRdc','CubvKyn4s14','RTwrhyLujcM','-eNWqcRKKKw'}
 for row in rows:
  row['source_candidates']=[]
  for link in links:
   if any(r.get('title') and r['title'].casefold() in link['published_context'].casefold() for r in row['references']):row['source_candidates'].append(link)
  row['availability']='candidate_identity_unverified' if row['source_candidates'] else 'source_not_established'
  row['youtube_probe']='access_blocked_2026-10-22' if row['id'] in blocked else 'not_probed'
  row['recovery']='Obtain ministry archive manifest/captions or import authorized local recording; verify teacher and exact lesson identity.'
 return {'checked':now(),'page':url,'page_sha256':hashlib.sha256(raw.encode()).hexdigest(),'listed_downloads':links,'videos':rows,'verified_exact_recording_sources':0,'note':'A matching title is a candidate, not evidence of identical recording or teacher. Unknown does not mean inaccessible.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--catalog',default='../dist/bible-teaching.json');p.add_argument('--bible',default='../dist/bible.json');p.add_argument('--out',default='reports');p.add_argument('--official',action='store_true');a=p.parse_args()
 atomic(Path(a.out)/'catalog-audit.json',catalog_audit(a.catalog,a.bible))
 if a.official:atomic(Path(a.out)/'source-availability.json',official_sources(a.catalog))
