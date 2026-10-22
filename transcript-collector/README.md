# Shepherd's Chapel transcript work (isolated branch)

This directory does not change the Illustrated KJV reader. It prepares a metadata-only queue from the existing `dist/bible-teaching.json`. Teachers are limited to Arnold Murray and Dennis Murray, with the original Scripture mapping preserved.

Run: `python transcript-collector/prepare_queue.py`

The companion GitHub Actions workflow is **manual, metadata-only**, without caption retrieval, scheduled runs, or permissions to publish transcripts. GitHub may require the workflow file to exist on the default branch before its manual dispatch appears in Actions; this branch is for safe review, not activation.

A verified live caption test, storage permissions and durable restricted transcript storage remain outstanding. Do not publish full lesson transcripts from this public repository.
