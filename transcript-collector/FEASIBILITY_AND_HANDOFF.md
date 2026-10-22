# Development and feasibility handoff — Build 008, October 22, 2026

## Decision

Free local transcription is technically viable for accessible recordings. Complete acquisition of the catalog is **not established**. The current public ministry audio listing is a rolling window, not a manifest for the entire historical collection. Do not begin a full-scale run or claim the archive is complete from this release.

This is a working source-based desktop engineering release with a real recognition pilot, not a fully certified end-to-end archive product. Exact recording identity, human audio accuracy review, a Dennis catalog lesson pilot, and complete source access remain release gates. The software reduces recurring transcription API cost to $0; it cannot create access rights or missing source media.

## Recovery evidence

- Repository: https://github.com/jeromeleegriffin/illustrated-kjv
- Existing isolated branch: `work/shepherd-transcript-collector`; recovered head `cd8a7f0622e25b1cd72a7f2f550b6dfb3e211ddc`.
- Existing draft PR: https://github.com/jeromeleegriffin/illustrated-kjv/pull/1 . No merge or production deployment.
- Read project brain, recovery/continuation documents, current status, teacher policy, reviewed owner audit, current catalog, collector scripts and workflow history.
- Build 007 recovered from `Shepherd_Chapel_Transcript_Collector_007.zip`. Original scripts, tests and README preserved in `legacy007/`. Its workflow was not activated. Useful catalog attribution, timestamp parsing, atomic persistence and bounded-retry concepts were retained and extended; SQLite replaces its best-effort JSON/cache state.
- Prior caption probe: https://github.com/jeromeleegriffin/illustrated-kjv/actions/runs/39726695028 . Job 119652119332 listed all five requests as access_blocked with return code 1. Its successful exit did not mean captions were obtained. Raw extractor errors were not retained in the report, so the precise network/platform root cause cannot be proved from that log alone.
- Prior catalog run: https://github.com/jeromeleegriffin/illustrated-kjv/actions/runs/39726522832 . Current deterministic import independently recalculates its numbers.
- Replaced recurring PR caption probing with offline Linux/Windows tests. No repeated blocked extraction, proxy rotation, cookie use, endpoint guessing or access-control bypass.

## Current catalog audit

`reports/catalog-audit.json` is recalculated from the actual repository files, not copied from stale reports:

| Measure | Result |
|---|---:|
| Bible books | 66 |
| Lesson-to-passage mappings | 1,304 |
| Unique recording IDs | 1,294 |
| Arnold Murray catalog attribution | 900 |
| Dennis Murray catalog attribution | 394 |
| Reuses of recording IDs across mappings | 10 |
| KJV dataset verses | 31,102 |
| Verses inside catalog passage ranges | 31,102 |
| Invalid passage bounds / missing mapped verses | 0 / 0 |

The ten reused mappings are not ten redundant media downloads. IDs are deduplicated. No conflicting teacher labels were found by import. However, 843 mapping records contain an inference marker somewhere in their saved metadata; the audit lists them for attribution review. This is a metadata provenance warning, not evidence that 843 teachers are wrong. Catalog attribution is not independent audio speaker verification.

Esther now uses `dDEZ3IyUfJk` for 1:1–6:14 and `BfNb2jswB_I` for 7:1–10:3, with owner-confirmed basis. `rwz3jeI2IFY` includes 1 Corinthians 6:12. `Y23KJsx-Kqc` maps 2 Thessalonians 2:7–17 and retains correction evidence. Older files saying these integrations were pending are historical. No catalog rewrite was performed.

## Official-source feasibility

Sources checked:
- https://shepherdschapel.com/audio
- https://shepherdschapel.com/video
- https://shepherdschapel.com/how-to-recieve
- https://shepherdschapel.com/booklist
- https://shepherdschapel.com/contact
- https://shepherdschapel.com/terms-of-service
- https://feeds.feedburner.com/ShepherdsChapel

The receive page documents a rolling five-day audio/podcast archive. The video page links YouTube playlists. No published full historical MP3 index or complete transcript archive was established in this audit. The podcast URL was not readable through the research tool. The book-list page supplies ordering/contact information but does not establish a complete digital audio package or a price for one. A full set of CDs/DVDs and educational archive access must be confirmed with the ministry; do not purchase or estimate an invented price.

The directly fetched live audio page differed from the search engine's cached version. It listed Divided, Mentorship, Repeat, Genesis 1:3–1:31, and Genesis 2:1–2:25. Only the latter two had exact catalog-title matches. Those are **candidates**, not verified identical video edits. The current source manifest enumerates every catalog ID: two candidates and 1,292 with no established direct source; it preserves the five earlier blocked YouTube probe results separately. This is a whole-catalog reconciliation against located sources, **not 1,294 successful network/access tests**.

The explicitly published Genesis 1:3–1:31 download, `http://shepherdsvod.oneconnxt.com/Audio/6830.mp3`, returned HTTP 200 with audio/mpeg and 28,092,545 bytes. It was used privately for the engineering pilot. Opening machine recognition identifies Arnold Murray. Exact equivalence to catalog video `J2Ia_1jDRdc` still needs comparison. No undocumented neighboring URLs were guessed. Public download availability is not a blanket license to redistribute full recordings/transcripts.

Site terms describe the ministry website and donations but do not explicitly grant bulk transcript republication. Copyright notices remain. A personal local pilot is kept private; obtain a specific archive/access and transcription response before a whole-collection acquisition arrangement. No external message has been sent.

## Paid-service research and reproducible architecture

Supadata documents native caption retrieval, AI generation, and automatic fallback; timestamped chunks use offsets/durations, larger work returns job IDs for polling. Batch endpoints accept video IDs, playlist or channel inputs and return per-item outcomes. These are publicly documented behaviors; the underlying media-access implementation is not disclosed by these sources. Our local queue, adapters, per-item statuses and caption-first/local-ASR path reproduce the general pipeline without buying the service. They do not reproduce undocumented platform access.

References: https://github.com/supadata-ai/skills/blob/main/skills/supadata/references/video.md and https://github.com/supadata-ai/skills/blob/main/skills/supadata/references/youtube.md . No paid credentials or calls used.

AssemblyAI requires a reachable direct audio/video file URL or an uploaded file. An ordinary watch page is not that media file. Its remote transcription pipeline therefore does not remove the need to acquire the source legitimately. Reference: https://www.assemblyai.com/docs/faq/what-types-of-audio-urls-can-i-use-with-the-api . Local files plus local ASR replace upload/remote computation here.

YouTube's official captions.download requires authorization and permission to edit the video. A viewer account is insufficient. The ministry could export caption files or arrange an authorized integration; this application currently imports those files rather than collecting OAuth credentials. Reference: https://developers.google.com/youtube/data/reference/rest/v3/captions/download . yt-dlp documents caption/media support and retry controls, but does not grant rights or ensure access. Reference: https://github.com/yt-dlp/yt-dlp . It is retained only in the recovered legacy collector, not automatically run by Build 008.

faster-whisper provides Python integration, CPU int8 and CUDA inference, VAD and timestamps. Selected for integration with the recovered Python project and maintainability. whisper.cpp is a viable C/C++ alternative with Windows and hardware acceleration support, but would require a second binary packaging/model interface. It is researched, not implemented. References: https://github.com/SYSTRAN/faster-whisper and https://github.com/ggml-org/whisper.cpp . Avoid interpreting their benchmark hardware as the owner's PC.

## Architecture and integrity

`prepare_queue.py`: strict teacher/ID catalog import, original passage ranges and mapping basis.
`audit.py`: independent KJV coverage calculation and published-link source reconciliation.
`engine.py`: SQLite WAL/full synchronous transactions, streaming audio decode, five-minute chunk checkpoints, local recognition, caption parsing, SHA-256 identity, FTS5 and JSON export.
`sources.py`: explicit approved manifests, local or direct-media URLs, teacher/identity/permission gates, bounded downloads, access-blocked stop status.
`app.py`: Tk desktop, single worker, main-thread UI event queue, source controls, viewer, search, settings and diagnostics.
`instance_lock.py`: OS process lock to prevent two app instances recovering the same state concurrently.

State flow: cataloged → ready after explicit source attachment → transcribing → quality_review after complete export. Interrupted work returns to ready; failures are separate. Unknown source identity never becomes verified complete. The database supports a verified_complete count but this release intentionally provides no automatic certification transition. All ASR text is labeled; silence/repetition/low-confidence/boundary warnings remain for review. No generated Bible verse replaces uncertain speech.

Complete byte acquisition does not prove semantic completeness. Five-minute boundaries may split words; overlap-aware alignment is future work. Caption-only final cues do not prove entire-recording length. The engine checks chunk continuity and export checksum but does not certify every audible word. Current search is lexical; curated topics, evidence-grounded Q&A and quizzes are future work and are not falsely represented as finished.

## Tests and pilot

`reports/automated-tests.txt`: 14 distinct tests for ingestion, timestamps, duplicate handling, teacher restrictions, search, corruption, persistence, chunk interruption and resumption. Synthetic fixtures are explicitly not ministry transcripts. The nine recovered Build 007 tests also pass when run from their original directory layout.

`reports/real-pilot.json`: genuine full-recording recognition metrics, checksums, reopen/search and structural validation. No full copyrighted transcript/audio is in this repository or package. Pilot content remains in private scratch; the report is durable metadata. A second process reopens the database to test persistence. A Windows CI job exercises catalog import, tests, actual Tk construction, selection, viewer and settings. Consult the actual run result before calling Windows verified.

A Dennis Murray catalog lesson has not been matched to a suitable authorized downloadable source in this run. No Dennis pass is claimed. No human listening comparison or word-error-rate measurement has been completed. The pilot does not count as a certified exact catalog transcript until identity and accuracy checks are satisfied.

## Time, storage and cost

API transcription fees: $0. No purchases or paid infrastructure were created. Installation/model downloads use bandwidth. The user's electricity price, PC power and hardware speed are unknown.

Planning example, **not measured total duration**: at 60 minutes per recording, 1,294 recordings imply 1,294 audio hours. At 64 kbps, compressed audio is about 37.3 GB; at 128 kbps about 74.5 GB. Keeping video can be much larger. Model/environment/cache add several GB. JSON/SQLite size depends on recognition output; allow 1–3 GB conservatively for text/index/history plus backups. The engine avoids retaining decoded WAV for the whole collection.

Processing estimate: measured real-time factor = pilot wall seconds / pilot audio seconds; multiply by actual total audio hours once durations are known. A base.en cloud CPU result is not a promise for small.en on Windows. Conservative planning at 0.5×–2× real time means 647–2,588 PC hours for the example collection. Electricity formula: hours × PC kW × local $/kWh. No unavoidable paid source price is known; seek a ministry quote before any approval request.

## Recovery plan and next release gates

1. Obtain a ministry-authorized historical audio/caption manifest with recording/series identifiers and Arnold/Dennis attribution. Ask specifically whether all catalog IDs can be matched, not just whether Bible books are available.
2. Reconcile the manifest and mark exact identity evidence. Keep alternate takes separate from original IDs. Confirm scope for personal transcription and future private quiz use; do not assume publication permission.
3. Complete Arnold audio comparison at opening, multiple middle points, boundaries and ending; transcribe a confirmed Dennis lesson and repeat.
4. Confirm Windows install and real inference on target hardware, including offline restart and disk-full behavior. Build a signed/portable executable only after dependencies and real-device behavior are validated.
5. Add boundary overlap alignment, fuller quality review UI and curated evidence-based topics. Keep recognized text and corrections separately versioned.
6. Only then authorize full processing against the verified source coverage report. Every missing/restricted item remains visible. Full archive completion requires all recordings accounted for and teaching coverage verified independently from metadata.

## Draft ministry request — NOT SENT

Dear Shepherd's Chapel,

I am Jerome Griffin. I am developing a private, noncommercial Bible-study and accessibility library using only Pastor Arnold Murray's and Pastor Dennis Murray's teachings. My existing catalog contains 1,294 distinct recordings associated with all 66 Bible books. I would like to transcribe authorized audio locally on my own Windows computer, retain timestamps and teacher attribution, and search it for personal study and quizzes. I will not publish or redistribute your recordings or full transcripts without express permission.

Could you provide or authorize access to a historical MP3 archive, downloadable book collections, existing captions/transcripts, or a recording manifest matching your series/lesson IDs to these recordings? The public audio page appears to offer a rolling five-day window. I can supply the catalog of video IDs and passage ranges for matching. Please clarify permitted automated download rate, personal transcription/storage use, whether alternate recordings are identical to the listed videos, and any cost before I commit. If digital archive access is unavailable, are lawful CD/DVD imports permitted, and what would the exact collection cost?

Thank you,
Jerome Griffin

Contact route published by ministry: https://shepherdschapel.com/contact and 1-800-643-4645. This request is prepared for owner review only; nothing was sent.

## Verified checkpoint

GitHub Windows and Ubuntu jobs passed in run https://github.com/jeromeleegriffin/illustrated-kjv/actions/runs/39730197002 . Windows Tk startup, all 1,294 catalog rows, selected-recording viewer and Settings were exercised. The Windows test did not run real audio inference or install the full speech dependency stack. The real audio pilot ran on Linux CPU: 3,510.048 seconds of audio, 536 segments, 17 warnings, 300.826 seconds of transcription; real-time factor 0.0857. A separate process reopened the saved database, found four search hits for beginning and passed structural checks. Full listening-based accuracy and exact video identity remain unverified.

### Windows installation and speech runtime gate passed

Run https://github.com/jeromeleegriffin/illustrated-kjv/actions/runs/39730444804 subsequently passed on Windows and Ubuntu. The Windows job installed the exact requirements file, downloaded/loaded base.en on CPU int8, performed real model inference on synthetic silence, and passed the desktop smoke test. This closes the earlier dependency-install uncertainty, but is not a Windows real-lesson accuracy test. Linux cached-model inference also passed with HF_HUB_OFFLINE=1. No fee-bearing transcription service was used.

### Browser caption breakthrough — October 22 continuation

The supported Work browser transcript exporter saved two actual official-channel
caption files: J2Ia_1jDRdc (Arnold, Genesis 1:3–1:31; 1,113 cues) and
2Q46edEZCp8 (Dennis, Leviticus 1:1–2:4; 1,022 cues). Both official page descriptions
confirm the respective teacher. Both imports reopened, passed structural checks,
and were searchable. These are caption imports, not new speech recognition runs.
See reports/browser-caption-pilot.json for hashes and observed timestamps.

This disproves treating the earlier GitHub Actions access result as evidence that
all captions are unavailable. The exporter reported no transcript for
2F0K2ip_82U; that result alone does not establish permanent absence. The remaining
catalog has not been checked through this route. No complete-source claim is made.

The collector now accepts the supported browser's timestamped .txt format. Video
ID headers must match the catalog. Times are preserved as start-only point markers
(end equals start, timing=start_only); no spoken end times are invented. Caption
machine-generation status is unknown rather than falsely declared human-authored.
Quality review remains required. Full private captions are excluded from git.

The browser exporter belongs to Work and is not a Windows runtime API. Automated
Windows acquisition and whole-catalog coverage remain unresolved. Do not promise
that this importer alone will automatically fetch all 1,294 lessons. Existing
Build 008 remains the current packaged release pending a cumulative tested update.

### Continued acquisition and Scripture audit — current checkpoint

Ten current-catalog IDs now have actual saved captions (10,014 timestamped
entries). All five formerly blocked GitHub probe recordings succeeded in the
supported Work browser. Several early exports reported unavailable before the
page/transcript was ready; after opening the visible transcript panel, they
succeeded. These are superseded results, not proof of missing captions or bot
blocking. The exact cause of the old GitHub extraction errors remains unknown.

The current per-ID overlay is reports/caption-availability.json: 10 saved and
1,284 not yet tested through this method. Original source-availability.json
remains a historical official-audio listing audit. No whole-catalog access
conclusion follows from this small sample. No new Windows acquisition adapter
is claimed: the Work export API is not available to the standalone desktop.

Actual captions also reveal a likely Esther mapping error. dDEZ3IyUfJk appears
to teach 1:1–2:23, although the catalog maps it through 6:14. The published
playlist contains omitted parts 2 (Zx0HS79ZCk0) and 3 (8eD3shcdgFE). Their captions
were recovered separately as candidates for chapters 3 and 4–6 respectively.
They are not silently counted among the 1,294 or inserted into production.
These third-party uploads have not been independently authenticated or granted
redistribution permission. Listening review is still needed. See
reports/scripture-caption-review.json for evidence timestamps and candidate IDs.

The 1 Corinthians correction has caption evidence for 6:12 at 32:22; the
2 Thessalonians correction has evidence for verse 17 at 33:47. These checks
support the existing corrected references but are not full audio validation.
The metadata union of 31,102 verses must not be described as verified teaching
coverage, particularly with the newly identified Esther discrepancy.

16 automated tests pass locally. The importer preserves auto-generated caption
labels and rejects malformed clock lines; authored-or-unspecified remains
unknown rather than human-certified. Ten private imports reopen and pass
structural checks. No full caption content is added to git. Build 008 remains
the sole packaged application; these changes continue on the draft branch.

### Broad access pass — 37 saved catalog transcripts

The subsequent pass attempted the first mapped recording for each of the 66
books, deduplicating the shared 2/3 John ID. Together with earlier pilot IDs,
72 distinct catalog recordings have now been attempted. Current outcomes are
37 saved and structurally verified (quality_review), 35 tested but unresolved,
and 1,222 not yet tested. This is a representative access pass, not a completed
whole-catalog access audit. The two Esther candidates remain separate.

Page-load and browser-operation timeouts, plus premature no-transcript export
results, account for unresolved attempts. Ruth, Philemon and Revelation
subsequently succeeded from ready pages. Do not convert these errors into
permanent missing-source labels or automatically retry them without bounds.
No explicit site-served bot challenge was observed during this pass. The old
GitHub extractor's root cause is still unknown.

caption_audit.py adds a resumable, local reconciliation command using existing
private exports and browser observations. It does not contact YouTube or pretend
to be a Windows retrieval adapter. It validates export IDs, parses timestamps,
imports through the existing database, verifies checksums, and emits counts for
every catalog ID. A successful browser status without a valid saved file never
counts as a transcript. Page-wide name occurrences are excluded from speaker
verification because recommendations may mention a different pastor.

17 local automated tests pass. Windows/Ubuntu run 39732767185 passed for the
preceding checkpoint. The new reconciliation code must be judged by its own CI
result. reports/breadth-caption-audit.json records actual counts, segment totals,
reopen/search results, and each book's representative outcome. Full copyrighted
caption text remains private, outside the repository. Source availability across
all 1,294 and independent Windows acquisition remain unresolved.

The broad import also exposed a real SQLite/FTS corruption incident in the
shared scratch workspace. Transcript checksums alone passed, but a reopened
search failed and PRAGMA integrity_check confirmed database corruption. Cause
is unknown; no SQLite, filesystem or application root cause is claimed. All
37 source exports remained intact. A separate active database was rebuilt from
them outside the browser-shared directory. Full SQLite integrity, FTS integrity,
reopening, and a 107-hit phrase search passed. The old database is preserved for
diagnosis. Verify Library now checks both SQLite and FTS, reports database_errors
and library_usable, and its synthetic corruption regression test passes. The
reconciler no longer rewrites existing transcript indexes unnecessarily. This
recovery does not prove the unknown original cause cannot recur.

## Recovery command and Exodus follow-up (2026-10-22)

Run 39735176610 completed successfully on Windows/Linux. Added `recover_captions.py`, which refuses existing destinations, copies source exports with hash checks, rebuilds independently, and reopens/verifies SQLite and search. Tested on 37 real exports; 18 local automated tests pass. This does not establish the cause of the earlier corruption or restore audio checkpoints.

A fresh public UI check of CEiN8_hTmcA (Exodus 1:1–2:16, official channel, description Pastor Arnold Murray) initially displayed captions unavailable. Expanding the description, opening Show transcript, and exporting succeeded. The validated file was imported: now 38 saved, 34 tested unresolved, 1,222 untested. This is still not a standalone Windows retrieval API or proof of complete coverage. All transcripts remain quality_review. See the current caption-availability report; earlier breadth/recovery reports describe their respective earlier snapshots.

## Standalone caption adapter experiment (2026-10-22)

Windows/Linux run 39735882613 passed for the previous recovery commit. Reopened Numbers iANFfv6DKhw and Joshua 4HgHsYjwhes through public UI, expanded description, opened transcript panel and saved valid exports. Current count: 40 saved, 32 unresolved, 1,222 untested. Catalog attribution is 34 Arnold / 6 Dennis; no independent voice certification.

Installed yt-dlp 2026.10.21 in an isolated probe directory. A single caption-only request for the same Numbers recording failed: HTTP 429, then bot-sign-in requirement. A missing-JavaScript-runtime warning also appeared; fixing that warning is NOT evidence that it resolves the access block. No access-bypass attempts or follow-up network retries were made.

Added `youtube_source.py` and a desktop button for caption-only collection where permission allows. It uses no cookies/proxies, bounded subprocess time, zero configured network retries, validates downloaded metadata ID and caption content, persists results, skips attempted/saved items, and holds the provider after an access denial. No recording without a saved caption is successful. 20 local tests pass; new adapter success tests are synthetic. Real standalone acquisition remains blocked and Windows retrieval unproven. This experimental adapter is on the branch, not yet in the Build 008 ZIP.
