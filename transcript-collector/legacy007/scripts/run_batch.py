#!/usr/bin/env python3
"""Run a bounded batch from the curated, teacher-attributed Bible catalog."""
import argparse, json, subprocess, sys
from pathlib import Path
from prepare_catalog import prepare
from collector import atomic

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--repo', default='.')
 p.add_argument('--out', default='transcript_output')
 p.add_argument('--limit',type=int,default=5)
 p.add_argument('--retrieve',action='store_true',help='Enable authorized transcript downloads')
 p.add_argument('--auto-captions',action='store_true')
 p.add_argument('--retry-failed',action='store_true',help='Retry videos previously marked failed')
 a=p.parse_args()
 repo=Path(a.repo); out=Path(a.out)
 source=repo/'dist'/'bible-teaching.json'
 if not source.exists():p.error('Cannot find curated catalog at '+str(source))
 out.mkdir(parents=True,exist_ok=True)
 catalog=out/'catalog-review.json'; rows=prepare(source,catalog)
 approval=out/'curated-approved.json'
 atomic(approval,{'approved_ids':[v['id'] for v in rows if v['teacher'] in ('Arnold Murray','Dennis Murray')]})
 cmd=[sys.executable,str(Path(__file__).with_name('collector.py')),'--catalog',str(catalog),'--out',str(out),'--approved',str(approval),'--limit',str(a.limit)]
 if a.retrieve:cmd+=['--collect']
 if a.auto_captions:cmd+=['--auto-captions']
 if a.retry_failed:cmd+=['--retry-failed']
 print('Curated catalog IDs:',len(rows),'network enabled:',a.retrieve,flush=True)
 return subprocess.call(cmd)
if __name__=='__main__':sys.exit(main())
