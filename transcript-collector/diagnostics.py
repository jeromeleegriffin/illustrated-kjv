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
