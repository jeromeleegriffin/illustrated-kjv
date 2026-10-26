# Griffin FAQ Batch Processor Build 001 — October 26, 2026

This is a working Windows companion for **saved transcripts → private FAQ candidates**. It is not a finished, independently verified FAQ archive or a replacement for the existing video collector.

## Actual Windows evidence

Windows CI: https://github.com/jeromeleegriffin/illustrated-kjv/actions/runs/40279794109

- Windows executable built with Python 3.12 / PyInstaller 6.16.0 and executed successfully.
- Frozen EXE HTTP test passed: startup, authorization, streamed ZIP import, persistent SQLite queue, private ZIP export and integrity.
- Frozen EXE in Windows Edge passed: actual page controls, file import, browser refresh/session recovery, pause, download, no JavaScript errors.
- Official Ollama v0.40.11 runtime download and SHA-256 validation passed on Windows. The free Qwen3 8B model downloaded and performed **real CPU inference**, correctly identifying a synthetic listener question and its source cue. Setup plus inference took 112.3 seconds on that runner. Synthetic captions were clearly labeled; private ministry transcripts were not sent to public CI.
- Existing collector tests passed on Linux and Windows, including Windows speech, native-caption fixture and old desktop smoke checks. The pre-existing CI ordering issue (PyAV missing before media tests) was corrected.
- Final evidence-hold guards have a regression test and are included in the cumulative release build. See the branch's latest workflow for its final build result.

## Actual private library evidence

- Imported the existing version-56 cumulative ZIP: **1,360 exports, zero invalid imports**, about 28 seconds on Linux.
- Read the existing baseline without modifying it: **1,356 approved FAQ groups; 2,141 linked answers**.
- Respected full-review, external assignment and teacher holds: **680 held, 680 eligible; 11,250 overlapping windows queued**. A hold does not mean failure or completed review.
- Two actual caption windows, from Arnold source fAT6qDIM_r8 and Dennis source 5EOrPMZ3ZTM, went through the real app worker and Qwen3 8B CPU model. Both windows saved; the private results reopened after database restart and exported successfully. Combined processing took **178.6 seconds** on this Linux host.
- Seven candidate listener questions were retained. **Two proposals were withheld** by the final evidence guards: an answer cut at a window edge, and a paraphrase exceeding its very short selected source evidence. Five remained unapproved machine candidates. None was added to the public FAQ registry. These are sampled windows, **zero fully reviewed recordings**, not a full-section recall/accuracy benchmark.
- Earlier Qwen2.5 3B and Qwen3 4B trials had duplication or cue-order failures. They were rejected as the release default. No claim of proprietary extraction methods is made.

## Automated coverage

Sixteen focused tests pass locally: interrupted-window recovery; unchanged import; changed-hash invalidation; completed-review and teacher holds; changing external reservations; archive path safety; start-only timestamps; bounded retry; ZIP integrity; full recording window coverage; rolling overlap; invented cue rejection; evidence preservation; malformed timestamps; withholding cut/thin-evidence answers; local API authorization and pause/export.

The whole recording is scanned in overlapping windows. This removes the old minute-30 assumption but cannot guarantee that a language model finds every listener question. Model notes and uncertainty are preserved. No model output becomes a human-reviewed or audio-verified answer automatically. Results stay private.

## Practical limits

- Windows 10 22H2+, 64-bit. **16 GB RAM recommended**, **14 GB free disk space** plus the private archive. No owner-PC test has occurred.
- The app ZIP bundles Python. No Python installation or pip commands are required from the owner.
- First setup can download **1.59 GB runtime + approximately 5.2 GB model**. Processing works locally after setup, with no paid transcription or language-model API.
- Windows must remain on and awake. Batch speed depends on hardware and caption length. At the sampled 89 seconds/window, 11,250 queued windows would take about **279 CPU hours / 12 continuous days**. This is a rough extrapolation, not a completion promise; empty teaching windows and GPU acceleration may be faster, long/failed windows slower.
- The release is unsigned. Windows security policy or antivirus can still block an unsigned EXE. Do not disable security controls.
- Full semantic review, speaker confirmation, question grouping, ranking and public publication remain required. Current Grok reservations are held rather than duplicated. This build does not reconcile the external Grok result files automatically.

Original captions, private evidence and the approved public FAQ registry remain unchanged. No production Bible, topical studies, Cloudflare pins or main branch were modified.

## Patch 1.0.1 — extended batch finding

A larger local CPU run saved six windows and 23 candidate questions, then the model server returned HTTP 500 / runner EOF while saving its prompt cache. Progress remained intact and the app paused. This is an extended-run failure that the original short pilot did not expose.

The resumed run uses a 4,096-token context and unloads the model after every window to bound retained model/cache memory. Patch 1.0.1 makes those settings the application default and records per-window processing settings in exports. This may add reload time. Do not describe the original short pilot as proof of indefinite unattended reliability. The current three-recording batch and its precise saved/failed windows are retained privately; only caption-reviewed paraphrases can enter the approved FAQ registry.

## Patch 1.0.2 — bounded quality-window recovery

The extended batch also exposed a dense Q&A window that exhausted the model output limit. Such output remains rejected. The processor now splits recoverable output/anchor failures into smaller overlapping windows automatically, records the split privately, preserves coverage through restart and stops subdivision at a bounded minimum. Eighteen focused tests include coverage-preserving split recovery and bounded retries. Failed or withheld content never becomes an approved public answer solely because a retry ran.

## Version 1.0.3

Added regression coverage for model-declared truncated/missing answers, empty-record completion, actual Controller recovery from malformed JSON using a controlled fake engine, and Windows sleep-request/release flags. Existing tests continue to cover source hashes, duplicate imports, interruptions, reservations, evidence and exports. Real model batch 003 is recorded separately as private evidence; machine outputs are not approved FAQs.

Version 1.0.4: real saved-caption testing found a model converting a listener statement into an invented why-question. Proposals with no explicit question/request signal in their selected question evidence are now withheld, with the original proposal retained privately. This is a conservative review guard, not proof that every other candidate is semantically valid; it can also hold legitimate questions requiring a wider source range. Added comment-vs-question and yes/no evidence regressions.


## Version 1.0.5 readiness check

Thirty-one focused tests now cover queue holds/releases, large-result paging, malformed segments, concurrent downloads and pause/reopen/resume. The release is rebuilt and executed on Windows, checked in Edge, and exercised with the official local AI. Separate private real-ministry excerpt tests verify pause and reopen without duplicate attempts; they are engineering checks, not new published FAQ approvals.

An export snapshot regression commits a worker result between the export’s SQL reads and verifies that no window disappears from the saved/unfinished accounting. Concurrent downloads are isolated and temporary files are removed.
