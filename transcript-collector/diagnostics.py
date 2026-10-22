import json,os,platform,shutil,sys
from pathlib import Path

def hardware():
 d={'platform':platform.platform(),'python':sys.version,'cpu_threads':os.cpu_count(),'recommended_device':'cpu','recommended_compute':'int8','cuda_devices':0}
 try:
  import ctranslate2
  d['cuda_devices']=ctranslate2.get_cuda_device_count()
  if d['cuda_devices']:d['cuda_note']='CUDA device found; cuBLAS/cuDNN compatibility still needs a real inference test.'
 except Exception as e:d['cuda_error']=str(e)
 return d
if __name__=='__main__':print(json.dumps(hardware(),indent=2))


def access_summary(root):
 """Readable, local-only report without transcript contents or credentials."""
 from collections import Counter
 root=Path(root)
 path=root/'youtube-source-report.json'
 if not path.exists():return 'No automatic access test has run yet. Enable authorized online downloads in Settings, then choose Test automatic caption access.'
 try:report=json.loads(path.read_text(encoding='utf-8'))
 except (OSError,ValueError):return 'The access report could not be read. Keep the original file for diagnosis; do not delete your library.'
 latest={r['id']:r for r in report.get('results',[])}
 counts=Counter(r.get('status','unknown') for r in latest.values())
 lines=['AUTOMATIC CAPTION ACCESS — LATEST RESULTS',f'Recordings tested: {len(latest)}',f'Saved for quality review: {counts.get("saved_quality_review",0)}','']
 messages={'rate_limited':'HTTP 429: requests are cooling down. Start / Resume waits for the saved deadline; after three rate-limit events, automatic requests stop.',
 'access_blocked':'YouTube blocked access. Automatic requests are paused; local audio transcription remains available.',
 'dependency_missing':'The downloader is missing. Run REPAIR_SETUP.bat, then preserve this report if the problem continues.',
 'timeout':'The request timed out. No transcript was counted as saved.',
 'no_english_caption_saved':'No supported English caption file was saved. This is not proof that the recording has no captions.',
 'request_failed':'The request failed. No transcript was counted as saved.',
 'failed':'Import or validation failed. No successful transcript is claimed.'}
 for status,count in sorted(counts.items()):
  lines.append(f'{status}: {count}')
  if status in messages:lines.append(messages[status])
 lines += ['', 'All saved transcripts still require accuracy and completeness review.', 'Technical details are in youtube-source-report.json in your private library folder.']
 return '\n'.join(lines)
