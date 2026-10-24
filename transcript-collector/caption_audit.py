"""Reconcile private saved exports and browser observations; makes no network requests."""
import argparse
import json
from collections import Counter
from pathlib import Path
from engine import Library, atomic, caption_metadata, digest, now, parse_captions, process
from prepare_queue import prepare

def reconcile(catalog, folder, library, observations=()):
    catalog_rows = prepare(catalog)
    known = {row['id']: row for row in catalog_rows}
    attempts = {}
    for observation in observations:
        vid = observation['id']
        if vid not in known:
            raise ValueError('Observation is outside the catalog: ' + vid)
        # A page-wide occurrence of a name is not speaker authentication.
        attempts.setdefault(vid, []).append({
            'status': observation.get('status'), 'title': observation.get('title'),
            'error': observation.get('error')})
    lib = Library(library, catalog)
    receipts, rejected, file_attempts = {}, [], set()
    try:
        for path in sorted(Path(folder).glob('*.txt')):
            vid = path.stem
            if vid not in known:
                rejected.append({'file': path.name, 'reason': 'Not in current catalog; keep as separate candidate'})
                continue
            file_attempts.add(vid)
            try:
                metadata = caption_metadata(path)
                if metadata.get('video_id') != vid:
                    raise ValueError('Export header does not match filename/catalog ID')
                segments = parse_captions(path)
                lib.attach(vid, path, 'Public caption export through supported Work browser. Private study; catalog attribution retained, not independently authenticated.')
                process(lib, vid)
                receipts[vid] = {
                    'sha256': digest(path), 'segments': len(segments),
                    'first_start': segments[0]['start'], 'last_start': segments[-1]['start'],
                    'caption_metadata': metadata}
            except Exception as exc:
                rejected.append({'file': path.name, 'reason': str(exc)})
        verification = lib.verify()
        invalid = {x['id'] for x in verification['failures']}
        entries = []
        for row in catalog_rows:
            vid = row['id']
            status = ('saved_quality_review' if vid in receipts and vid not in invalid else
                      'tested_unresolved' if vid in attempts or vid in file_attempts else 'not_tested_with_this_method')
            if vid in invalid:
                status = 'integrity_failed'
            entry = {'id': vid, 'teacher': row['teacher'], 'caption_status': status}
            if vid in receipts:
                entry.update(receipts[vid])
            if vid in attempts:
                entry['attempts'] = attempts[vid]
            entries.append(entry)
        counts = dict(Counter(r['caption_status'] for r in entries))
        result = {
            'checked': now(), 'catalog_sha256': digest(catalog),
            'total_unique_recordings': len(entries), 'counts': counts,
            'verified_complete': 0, 'verification': verification, 'rejected_files': rejected,
            'recordings': entries,
            'note': 'File-backed evidence only. Browser success without a validated saved file never counts as a transcript. Unresolved does not mean unavailable. Catalog teacher labels are not independent speaker verification. No Windows retrieval or full Scripture-coverage claim.'}
        return result
    finally:
        lib.close()

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--catalog', required=True)
    p.add_argument('--folder', required=True)
    p.add_argument('--library', required=True)
    p.add_argument('--observations')
    p.add_argument('--out', required=True)
    args = p.parse_args()
    observations = json.loads(Path(args.observations).read_text(encoding='utf-8')) if args.observations else []
    report = reconcile(args.catalog, args.folder, args.library, observations)
    atomic(args.out, report)
    print(json.dumps({'counts': report['counts'], 'verification': report['verification'], 'rejected_files': report['rejected_files']}, indent=2))
