"""Windows CI: real official runtime download, local model pull and CPU inference.
Only synthetic test captions are used. No private ministry transcripts leave the host.
"""
import json,sys,tempfile,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import Controller
from core import Ollama,validate_result

def main():
 with tempfile.TemporaryDirectory() as tmp:
  c=Controller(tmp)
  try:
   start=time.time();c.setup();assert 'ready' in c.message.lower()
   d={'id':'abcdefghijk','teacher':'Arnold Murray','duration':65,'segments':[
    {'start':0,'end':5,'text':'SYNTHETIC SOFTWARE TEST ONLY. This is not an actual pastor recording.'},
    {'start':5,'end':10,'text':'Let us move to listener question time.'},
    {'start':10,'end':20,'text':'Mary from Texas asks: What does the word rest mean?'},
    {'start':20,'end':35,'text':'The answer is that rest means stopping work and taking a break.'},
    {'start':35,'end':45,'text':'That finishes the answer to Mary. We are out of time for questions.'},
    {'start':45,'end':65,'text':'End of this synthetic software test.'}]}
   window={'start':0,'end':65,'cues':[{'i':i,**s} for i,s in enumerate(d['segments'])]}
   engine=Ollama();engine.hardware='cpu';raw,metrics=engine.extract(window,d['teacher']);rows=validate_result(d,window,raw)
   assert len(rows)==1,raw
   assert 'rest' in rows[0]['question'].lower() and 'work' in rows[0]['answer'].lower(),raw
   assert rows[0]['question_first_cue']==2 and rows[0]['answer_first_cue']==3,raw
   assert not rows[0]['audio_verified']
   print(json.dumps({'test':'Windows official runtime + real local CPU AI','passed':True,'elapsed_seconds':round(time.time()-start,1),'model':engine.model,'eval_count':metrics.get('eval_count')}))
  finally:
   c.close()

if __name__=='__main__':main()
