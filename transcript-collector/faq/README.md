# FAQ frequency update — October 24, 2026

The public FAQ contains 12 question groups, 81 linked reviewed source occurrences and 79 counted recording groups across68 videos. Counts are lower bounds from reviewed passages, not whole-archive frequencies. One question is counted once per underlying recording. Two reviewed alternate-upload pairs are linked and counted once; three known identical Peter-caption pairs are retained in the alias registry for future use.

1360 private exports are tracked:1291 passage-catalog transcripts,65 topical candidates and4 recovery supplements. All were scanned for question candidates.68 recordings have selected reviewed passages; zero recordings have completed full Q&A review.65 topical exports remain excluded from published answers pending teacher attribution. Private candidates are not facts or approved FAQ entries.

Public answers are short editorial paraphrases with separate pastor attribution, variants and timestamped original-video links. No raw transcript text, downloaded media or credentials belongs in this repository.

## Incremental update

After importing a new transcript batch into the private library:

    python3 transcript-collector/faq/update_faq.py --library PRIVATE_LIBRARY --dist dist

In this development workspace the equivalent script is `faq-development/scripts/update_faq.py`; registry is `faq-development/reviewed-occurrences.json`. In the repository the script and registry live together under `transcript-collector/faq/`; pass `--registry transcript-collector/faq/reviewed-occurrences.json` explicitly.

The private SQLite progress database stores videoID, export hash, scanner version and scan time. Unchanged files skip rescanning. New/changed files produce private candidate files. Editing the reviewed registry is a separate passage-review step; scanning never approves an answer or generates a quotation. Changed hashes invalidate approved occurrences until rechecked. Source-missing rows remain in the tracking ledger.

Keep distinct questions separate. Preserve different answers as separate variants. New approved occurrences recalculate ranks automatically. Review suspected alternate uploads before adding aliases; never deduplicate merely because the topic matches.

## Checks

Real-corpus rebuild:1360 files;68 partially reviewed;12 question groups;79 counted recording groups. Second run:1360 unchanged,zero new scans, unchanged frequencies. Unit tests cover duplicate-group counting, restart/idempotence, changed-source approval invalidation and newly added files. Local browser download was unavailable; live browser verification is recorded separately.

## Deployment scope

Update only the six FAQ assets through a separate immutable FAQ release pin on the existing Bible Worker. Keep the production Bible asset release pin and other routes unchanged. Do not merge main or deploy GitHub Pages. Preserve the pre-update Worker for rollback.
