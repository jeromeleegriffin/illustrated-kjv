"""OS-held lock released automatically on crash; prevents concurrent recovery."""
import os
class InstanceLock:
 def __init__(self,path):
  path.parent.mkdir(parents=True,exist_ok=True);self.file=open(path,'a+b');self.file.seek(0);self.file.write(b'0');self.file.flush();self.file.seek(0)
  try:
   if os.name=='nt':
    import msvcrt
    msvcrt.locking(self.file.fileno(),msvcrt.LK_NBLCK,1)
   else:
    import fcntl
    fcntl.flock(self.file.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
  except OSError:
   self.file.close();raise RuntimeError('Collector is already running. Close the other window first.')
 def close(self):self.file.close()
