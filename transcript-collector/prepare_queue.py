#!/usr/bin/env python3
"""Generate a deterministic, teacher-attributed queue from the existing Bible mapping.
Does not request captions or modify the Bible reader.
"""
import argparse, json, re
from pathlib import Path

def prepare(source):
    data=json.loads(Path(source).read_text(encoding="utf-8"))
    videos={}
    for book in data.get("books",[]):
        for lesson in book.get("lessons",[]):
            vid=lesson.get("id")
            teacher=lesson.get("teacher")
            if not isinstance(vid,str) or not re.fullmatch(r"[A-Za-z0-9_-]{11}",vid):
                raise ValueError("Invalid catalog ID: "+repr(vid))
            if teacher not in ("Arnold Murray","Dennis Murray"):
                raise ValueError("Unapproved teacher: "+repr(teacher))
            row=videos.setdefault(vid,{"id":vid,"teacher":teacher,
                "url":"https://www.youtube.com/watch?v="+vid,"references":[]})
            if row["teacher"]!=teacher:
                raise ValueError("Conflicting teacher labels for "+vid)
            row["references"].append({"book":book.get("name"),
                "title":lesson.get("title"),"start":lesson.get("start"),"end":lesson.get("end"),"mapping_basis":lesson.get("mappingBasis"),"official":lesson.get("official",False)})
    return list(videos.values())

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--catalog",default="dist/bible-teaching.json")
    p.add_argument("--out",default="transcript-work/approved-candidates.json")
    a=p.parse_args()
    videos=prepare(a.catalog)
    out=Path(a.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"schema":"shepherd-candidates-v1",
        "source":a.catalog,"note":"Catalog candidates only; no transcript processing permission asserted.",
        "videos":videos},indent=2)+"\n",encoding="utf-8")
    print("Catalog videos:",len(videos),"Arnold:",sum(v["teacher"]=="Arnold Murray" for v in videos),
          "Dennis:",sum(v["teacher"]=="Dennis Murray" for v in videos))
    print("Wrote",out)

if __name__=="__main__": main()
