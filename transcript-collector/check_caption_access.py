#!/usr/bin/env python3
"""Check caption availability for five curated lessons; never persist transcript text."""
import json, subprocess, sys
from pathlib import Path

def main():
    doc=json.loads(Path("transcript-work/approved-candidates.json").read_text())
    sample=doc["videos"][:5]
    outcomes=[]
    for row in sample:
        video_id=row["id"]
        cmd=["yt-dlp","--skip-download","--list-subs","--no-playlist","--socket-timeout","15",
             "--retries","1","--",row["url"]]
        try:
            proc=subprocess.run(cmd,text=True,capture_output=True,timeout=60)
            out=proc.stdout
            has_captions=("Available subtitles" in out or "Available automatic captions" in out)
            status="captions_listed" if proc.returncode==0 and has_captions else ("no_captions_listed" if proc.returncode==0 else "request_failed")
            err=(proc.stderr or "").lower()
            if "sign in" in err or "bot" in err: status="access_blocked"
            outcomes.append({"id":video_id,"teacher":row["teacher"],"status":status,"returncode":proc.returncode})
        except subprocess.TimeoutExpired:
            outcomes.append({"id":video_id,"teacher":row["teacher"],"status":"timeout"})
    Path("transcript-work/caption-availability-report.json").write_text(json.dumps({"type":"availability_only","videos":outcomes},indent=2)+"\n")
    print(json.dumps(outcomes,indent=2))
    if not any(x["status"]=="captions_listed" for x in outcomes):
        print("WARNING: No successfully listed captions; network or platform access may be restricted.",file=sys.stderr)

if __name__=="__main__": main()
