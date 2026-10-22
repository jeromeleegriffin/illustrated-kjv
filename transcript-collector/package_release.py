"""Build the cumulative source-based Windows ZIP, excluding private runtime data."""
from pathlib import Path
import argparse
import zipfile


def build(destination):
    base = Path(__file__).resolve().parent
    catalog = base.parent / 'dist' / 'bible-teaching.json'
    destination = Path(destination)
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as z:
        # Include tracked source/documentation only; never sweep user databases/media.
        import subprocess
        paths = subprocess.check_output(['git','ls-files','transcript-collector'],cwd=base.parent,text=True).splitlines()
        for name in paths:
            path = base.parent / name
            z.write(path, path.relative_to(base))
        z.write(catalog, 'catalog.json')
    with zipfile.ZipFile(destination) as z:
        assert z.testzip() is None
        for name in ['index.html','START_HERE.bat','app.py','engine.py','youtube_source.py','catalog.json','READ_FIRST.txt']:
            assert name in z.namelist(), name
        assert not any(n.endswith(('.sqlite','.mp3','.mp4')) for n in z.namelist())
    return destination

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination')
    print(build(parser.parse_args().destination))
