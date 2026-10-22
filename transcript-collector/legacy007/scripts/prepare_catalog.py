#!/usr/bin/env python3
"""Generate a precise review manifest from Illustrated KJV's curated mapping."""
import argparse,json,re
from pathlib import Path
from collector import atomic,vid,utc

VALID=re.compile(r'^[A-Za-z0-9_-]{11}$')
TEACHERS={'Arnold Murray','Dennis Murray'}

def prepare(src,dest):
    data=json.loads(Path(src).read_text(encoding='utf-8'))
    if not isinstance(data,dict) or not isinstance(data.get('books'),list):
        raise ValueError('Expected authoritative bible-teaching.json with a books array')
    found={}; invalid=[]; mapping_count=0
    for book in data['books']:
        if not isinstance(book,dict):continue
        book_name=book.get('name','Unknown')
        for lesson in book.get('lessons',[]):
            mapping_count+=1
            video_id=lesson.get('id')
            url=lesson.get('url') or ('https://www.youtube.com/watch?v='+str(video_id))
            if not isinstance(video_id,str) or not VALID.fullmatch(video_id) or vid(url)!=video_id:
                invalid.append({'book':book_name,'id':video_id,'reason':'invalid ID or mismatched URL'});continue
            teacher=lesson.get('teacher')
            if teacher not in TEACHERS:
                invalid.append({'book':book_name,'id':video_id,'reason':'unverified teacher'});continue
            row=found.setdefault(video_id,{'id':video_id,'url':'https://www.youtube.com/watch?v='+video_id,'teacher':teacher,'title':lesson.get('title',''),'book_passages':[], 'official':bool(lesson.get('official',False)), 'source':'dist/bible-teaching.json'})
            if row['teacher']!=teacher:
                invalid.append({'book':book_name,'id':video_id,'reason':'conflicting teacher'});continue
            passage={'book':book_name,'start':lesson.get('start'),'end':lesson.get('end')}
            if passage not in row['book_passages']: row['book_passages'].append(passage)
    rows=list(found.values())
    manifest={'schema':'shepherd-approved-candidates-v1','source':str(src),'generated_utc':utc(),'mapping_count':mapping_count,'total_distinct':len(rows),'teacher_counts':{t:sum(v['teacher']==t for v in rows) for t in sorted(TEACHERS)},'invalid':invalid,'videos':rows,'note':'Catalog review only. Captions have not been retrieved. Authorization to store transcript text must be established separately.'}
    atomic(Path(dest),manifest)
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--out',default='catalog-review.json');a=p.parse_args()
    src=Path(a.repo)/'dist'/'bible-teaching.json'
    if not src.is_file():p.error('Missing catalog: '+str(src))
    rows=prepare(src,a.out)
    print('Prepared',len(rows),'unique curated lessons; no network access or caption retrieval.')
if __name__=='__main__':main()
