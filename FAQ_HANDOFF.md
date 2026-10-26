# Teaching FAQ development checkpoint

Adds an isolated FAQ page to the existing Bible reader menu on `work/shepherd-transcript-collector`. Main and production Pages are not deployed or merged. Only a new FAQ anchor was inserted into each existing reader entry page; all other reader markup is preserved. Existing KJV data, catalog, reading storage, study tools and scripts are untouched.

Seven initial editorial paraphrases have seven caption evidence ranges across four Arnold Murray recordings. They are not verbatim quotations or independent audio verification. They are an initial selection, not frequency rankings or all Q&A from609 lessons. The ledger records609 available transcripts: four partially reviewed,605 pending, zero fully reviewed. Two duplicate-content Exodus IDs remain quarantined in the private library and are not represented as processed FAQ sources.

## Sources and variants

`dist/teaching-faq.json` stores stable question IDs, separate answer IDs, teacher, editorial summary, cited Scripture mentions, source video IDs, start/end seconds, source-file and transcript SHA256, and a hash of the exact selected segment array. Full copyrighted transcripts and audio are private and are not committed. The frontend supports multiple answer variants under one question, prioritizes Arnold, and can flag `conflict_needs_review` without merging conflicting teaching. Dennis remains clearly attributed fallback. No automatic semantic merging or conflict resolution is claimed.

`dist/teaching-faq-review.json` is the durable per-recording ledger. It records video ID, catalog title, teacher, transcript and source hash, question IDs, reviewed timestamp ranges, current status and change history. Partial review does not imply the remainder of a recording has been checked. Fully reviewed is an explicit editorial status; scanning never sets it.

## After every incoming transcript batch

Run from the repository root, pointing at the actual private transcript JSON export directory:

```
python scripts/faq_review.py --transcripts PRIVATE/search-library/transcripts --faq dist/teaching-faq.json --ledger dist/teaching-faq-review.json
```

The command queues new IDs, preserves prior review state on unchanged files, flags changed source versions and stale answers, and retains missing sources as source_missing. It rebuilds teaching-faq-data.js for the static page. It does not contact websites or publish private captions. Commit the updated metadata ledger and reviewed summaries to this isolated branch after checking them.

For each queued source, inspect all lesson Q&A before explicitly marking the full recording reviewed. Add new evidence to an existing stable question only after confirming the same intent; preserve separate answer variants for qualifications or differences. Record teacher, source version and timestamp window for every answer. A changed transcript requires rechecking the evidence; do not refresh source hashes simply to clear warnings. Retain any contradictory answer and flag it for review. The current scan is operator-invoked after imports, not yet wired automatically into the Windows collector.

## Verification

Five Python tests cover incremental new/unchanged/changed/missing input and explicit full-review preservation. Node DOM tests exercise seven cards, search, timestamp link, pastor filtering/empty state/reset and609 ledger rows/filter. JS syntax passes; entry-page preservation was checked by removing the sole added anchor and comparing the original byte text. All seven IDs, source hashes and ranges resolve against retained private transcripts.

Visual browser testing is pending: Playwright is installed but Chromium is absent; the browser download returned an invalid ZIP. No actual Windows/Android rendering pass is claimed. The stylesheet includes responsive layouts; device QA is required before deployment.

The standalone review ZIP's root index.html embeds the page styles/data/script, opens offline, and links back to the existing live Bible reader. It is an FAQ-only review package, not a replacement distribution of the full Bible app. Full source changes remain in the draft PR. Existing cumulative private transcript ZIP remains separate and unchanged.
