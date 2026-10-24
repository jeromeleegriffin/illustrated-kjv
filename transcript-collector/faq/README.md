# Shepherd’s Chapel FAQ review

Current approved registry: 717 question groups and 1,099 linked answer occurrences. Frequencies are lower bounds from reviewed passages, counted once per question per underlying recording group.

All 1,360 private exports have been scanned for candidates. Three recordings have complete caption Q&A reviews, 120 remain partially reviewed, 1,172 await passage/supplement review and 65 topical exports await teacher confirmation. Scanning never approves answers. Caption review is not independent audio verification.

## Rebuild

Run `python3 transcript-collector/faq/update_faq.py --library PRIVATE_LIBRARY --dist dist --registry transcript-collector/faq/reviewed-occurrences.json`. Keep transcripts, media and candidate excerpts private. Commit only paraphrases, code and sanitized metadata.

Occurrences bind teacher, video, exact caption anchors and transcript hash. Changed hashes invalidate approval. Preserve answer variants and documented recording aliases. The `recording_reviews` array stores explicit Q&A boundaries, reviewed ranges, unresolved ranges and a resume cursor; only contiguous complete review with confirmed boundaries qualifies as fully reviewed. Never infer completion from occurrence presence.

## Validation and publication

Run tests under `transcript-collector/faq/tests`. Verify duplicate counting, distinct variants, resume, hash invalidation and completion evidence. Rebuild frequency ranking and source ledger from approved occurrences.

Publish only the six FAQ assets using the separate FAQ release pin on the existing Bible Worker. Read the current Worker and settings before changing that pin; preserve the Bible release and unrelated routes. Never merge main, deploy GitHub Pages or commit full transcript copies.
