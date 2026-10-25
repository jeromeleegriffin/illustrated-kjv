# Shepherd’s Chapel FAQ review

Current approved registry: 1,204 question groups and 1,854 linked answer occurrences. Frequencies are lower bounds from reviewed passages, counted once per question per underlying recording group.

All 1,360 private exports have been scanned for candidates. Fifteen recordings have complete caption Q&A reviews, 154 remain partially reviewed, 1,126 await passage/supplement review and 65 topical exports await teacher confirmation. Scanning never approves answers. Caption review is not independent audio verification.

## Rebuild

Run `python3 transcript-collector/faq/update_faq.py --library PRIVATE_LIBRARY --dist dist --registry transcript-collector/faq/reviewed-occurrences.json`. Keep transcripts, media and candidate excerpts private. Commit only paraphrases, code and sanitized metadata.

Occurrences bind teacher, video, exact caption anchors and transcript hash. Changed hashes invalidate approval. Preserve answer variants and documented recording aliases. The `recording_reviews` array stores explicit Q&A boundaries, reviewed ranges, unresolved ranges and a resume cursor; only contiguous complete review with confirmed boundaries qualifies as fully reviewed. Never infer completion from occurrence presence.

## Validation and publication

Run tests under `transcript-collector/faq/tests`. Verify duplicate counting, distinct variants, resume, hash invalidation and completion evidence. Rebuild frequency ranking and source ledger from approved occurrences.

Publish only the six FAQ assets using the separate FAQ release pin on the existing Bible Worker. Read the current Worker and settings before changing that pin; preserve the Bible release and unrelated routes. Never merge main, deploy GitHub Pages or commit full transcript copies.

## External extraction assignments

Before selecting another new recording batch, inspect `external-review-assignments.json`. Set griffin-faq-grok-300-20261024-A has returned 300 result files with 4,641 question candidates in checkpoint 042. All hashes and caption anchors passed independent structural checks. Seventeen result recordings have been semantically reviewed here (293 approved linked answers; twenty-two candidates held; one rhetorical extension and one listener thanks excluded), one additional incomplete export is blocked, and 282 result recordings await semantic review. These results are reserved for reconciliation, not blanket-approved. External completion claims never replace current reviewed statuses. Imported results must retain their source hashes, caption evidence, full-Q&A coverage and precise cursor; structural validation alone does not approve teaching paraphrases or confirm speakers.

## Attribution hold

Do not approve `4pmWjZmHK1o` under the saved Arnold attribution: its named introduction and listener address identify Dennis. The original source remains unchanged. See the sanitized pass028 report and private attribution-holds checkpoint before further review.

## Recovered private batch

The39-answer Dennis checkpoint libfile_3a9e3631e500819183ae10f3f780a8e2 has been reconciled idempotently with the current registry. Sources5EOrPMZ3ZTM and5FJ-a7O6PL8 have complete caption Q&A reviews, audio pending. Do not import or count those39 occurrences again.


## Second external assignment

Set `griffin-faq-grok-300-20261025-B` reserves another 300 previously unreviewed Arnold Murray passage exports, excluding assignment A, reviewed records, known alias groups and attribution holds. Package: `Griffin_Grok_FAQ_300_Recordings_002.zip`. All 300 remain pending; preparation is not a completed review and does not change published FAQ counts. The package supplies untouched transcripts, cue-indexed reading aids, the full prompt and tested structural validators. Actual presenter, source completeness and semantics still require review.


## Cross-recording difference

Pass039 flags a difference concerning spiritual activity attributed to restrained fallen angels: djw2r6xERR4 allows it, while dClenWFh8sM had denied it in an earlier answer. Keep both source-bound variants and the related dsxz1k0gvew distinction; do not harmonize them without further review. All remain audio-pending.

## Fixed FAQ navigation

Pass041 anchors both paging bars to the viewport, reserves space above and below the question, and retains the existing button nodes so focus survives paging. Page changes return the answer to its start. Question length and expanded answers no longer determine the button positions.
