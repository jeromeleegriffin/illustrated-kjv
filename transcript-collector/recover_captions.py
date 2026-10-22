"""Rebuild a separate library from preserved Work caption exports, offline."""
import argparse
import json
import shutil
from pathlib import Path
from caption_audit import reconcile
from engine import Library, atomic, digest


def rebuild(catalog, source, destination):
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if not source.is_dir():
        raise ValueError('Caption source directory does not exist')
    files = sorted(source.glob('*.txt'))
    if not files:
        raise ValueError('No preserved caption .txt exports found')
    # Never open or modify an existing (possibly damaged) library.
    # mkdir is exclusive, including against another recovery process.
    destination.mkdir(parents=True, exist_ok=False)
    copies = destination / 'caption-sources'
    copies.mkdir()
    hashes = {}
    for path in files:
        before = digest(path)
        target = copies / path.name
        shutil.copyfile(path, target)
        if digest(target) != before or digest(path) != before:
            raise ValueError('Source changed during recovery: ' + path.name)
        hashes[path.name] = before
    report = reconcile(catalog, copies, destination)
    lib = Library(destination)
    try:
        integrity = [r[0] for r in lib.db.execute('PRAGMA integrity_check')]
        # Exercise the persisted index after reopening, even with zero results.
        lib.find('beginning')
    finally:
        lib.close()
    report['recovery'] = {
        'source_files_unchanged': all(digest(source / name) == sha for name, sha in hashes.items()),
        'copied_sources': hashes, 'sqlite_integrity': integrity,
        'existing_database_modified': False,
        'scope': 'Browser caption exports only; audio checkpoints, settings and prior review decisions are not restored.'}
    report['recovery']['usable'] = bool(
        report['verification']['library_usable'] and integrity == ['ok'] and
        report['recovery']['source_files_unchanged'] and
        report['counts'].get('saved_quality_review', 0) > 0)
    atomic(destination / 'recovery-report.json', report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', required=True)
    parser.add_argument('--source', required=True)
    parser.add_argument('--destination', required=True, help='Must be a NEW directory')
    args = parser.parse_args()
    result = rebuild(args.catalog, args.source, args.destination)
    print(json.dumps({'counts': result['counts'], 'usable': result['recovery']['usable'],
                      'rejected_files': result['rejected_files']}, indent=2))
    raise SystemExit(0 if result['recovery']['usable'] else 1)
