# Shepherd's Chapel Transcript Collector | Build 007

Continues existing Build 004. **No live Bible files changed; no deployment and no real captions retrieved.**

## Actual catalog verified

On October 22, 2026, the GitHub blob endpoint returned `dist/bible-teaching.json` from `jeromeleegriffin/illustrated-kjv`, revision 009. Direct inspection found **66 books, 1,304 passage mappings, 1,294 distinct recordings**: **900 Arnold Murray**, **394 Dennis Murray**. All 1,304 mappings had valid 11-character YouTube IDs; none were invalid by ID format. These numbers describe catalog entries, **not accessible transcripts**.

## Prepare for batch retrieval, without manual link gathering

In an extracted checkout of `illustrated-kjv` on Windows, run from this collector directory:

```powershell
py scripts/prepare_catalog.py --repo "C:\path\to\illustrated-kjv" --out catalog-review.json
py scripts/collector.py --catalog catalog-review.json --out transcript_output
```

These commands work offline and create `catalog-review.json`, `transcript_output/manifest.json` and a review template. Unlike prior versions, **use catalog-review.json as the collector input**, not the original `bible-teaching.json`. This guarantees it receives actual video links with known teacher identity.

After confirming transcript storage/reuse permission, copy `transcript_output/approval-template.json` to `approved.json` and add selected confirmed IDs to `approved_ids`. Install `yt-dlp` using `py -m pip install -U yt-dlp`. Then try a small batch:

```powershell
py scripts/collector.py --catalog catalog-review.json --out transcript_output --collect --approved approved.json --auto-captions --limit 5
```

Repeat in larger batches as desired. Successful videos are skipped, failed videos are recorded, and retried only with `--retry-failed`. Keep transcript outputs private unless you have permission to publish them. YouTube may reject caption access, or a video may have no captions.

## Tests

`py -m unittest discover -s tests -v`

The root `index.html` is an informational start page, not a browser-hosted transcript downloader. Running collection requires Python and outbound internet access. No scheduled collection is yet enabled.

## Build 006: unattended runner (not yet installed)

The package adds `scripts/run_batch.py` and `.github/workflows/shepherd-transcripts.yml`. To install them, place these paths in the **illustrated-kjv** repository without overwriting the Bible app. The workflow's scheduled job is **gated off** until repository variable `SHEPHERD_TRANSCRIPT_PERMISSION_CONFIRMED` is explicitly set to `true` after permission to retain/process captions is confirmed. It processes at most 5 videos per scheduled run and uses GitHub Actions cache for best-effort recovery; caches are not permanent storage and may expire. Reports are uploaded for 30 days. A more durable private store is needed for the full 1,294 videos. No paid speech transcription is included and YouTube extraction may fail. No live site deployment is involved.

Dry run from the repository checkout with the collector scripts in place:

`python scripts/run_batch.py --repo . --out transcript_output --limit 5`

For authorized caption retrieval:

`python scripts/run_batch.py --repo . --out transcript_output --limit 5 --retrieve --auto-captions`

## Build 007 reliability improvements

The scheduled runner can now use `--retry-failed`. First-time videos are prioritized over older failures; failed captions are attempted at most three times in total to prevent repeated unavailable videos from consuming every run. Reports now record `failed_this_run`. The GitHub workflow prints a batch outcome summary. This is a local, isolated candidate only: no job has been installed or activated in GitHub, and **no real captions have yet been downloaded or authorized for archiving**.

For the next real-world test, verify permission to retain/process captions, install scripts and workflow on a separate branch, and manually dispatch the job with the permission variable enabled. The GitHub Actions cache is not a long-term private archive; plan durable restricted storage before processing the whole catalog.
