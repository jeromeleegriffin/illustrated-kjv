"""Real Tk construction, selection and settings smoke test on Windows CI."""
import os,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
with tempfile.TemporaryDirectory() as folder:
 import app
 app.CONFIG=Path(folder)/'location.json';app.CONFIG.write_text(__import__('json').dumps({'output':folder}))
 root=app.tk.Tk();application=app.App(root);root.update()
 assert len(application.tree.get_children())==1294
 first=application.tree.get_children()[0];application.tree.selection_set(first);application.view();root.update()
 assert 'Arnold Murray' in application.viewer.get('1.0','end')
 application.settings();root.update()
 application.close()
 print('PASS: Tk launch, full catalog, selection, viewer and settings')
