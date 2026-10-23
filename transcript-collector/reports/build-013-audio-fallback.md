# Build 013 development checkpoint — 2026-10-23

Continues Build 012, preserving the catalog, existing private data and all provider holds. Not yet a validated Windows release.

Implemented an opt-in Settings control for original English audio fallback. Start / Resume checks up to ten new caption requests per pass, then attempts up to ten previously identified missing-caption recordings and transcribes each available recording locally. Existing ready sources are still processed. Further batches require Start / Resume. Audio failures are retained in youtube-audio-report.json and not automatically retried; manual investigation is currently required to requeue a failed audio attempt. Caption retries retain existing policy.

Audio selection requires English language plus an explicit original-track marker. Ambiguous tracks are left unresolved. Downloads have file/disk limits, no automatic retries, and a 15-minute subprocess timeout. Pause waits for the current download/validation or timeout, then the existing ASR chunk checkpoint. No proxy, cookies, account switching or restriction bypass. Caption provider blocks and rate-limit ceilings also hold the audio adapter.

Before attaching audio, the worker rejects empty/webpage responses and decodes the entire audio stream with PyAV, checking decoded duration against metadata (3 seconds or 1 percent tolerance). A SHA-256 receipt supports reuse after interruption. Media verification does not establish transcript accuracy, speaker identity or source rights. The existing local faster-whisper pipeline saves machine transcripts for quality review, not verified complete.

## Evidence

39 local automated tests passed, including four new tests: original English selection excluding dubbed tracks; HTML-as-audio rejection; decoding a generated 5-second WAV and rejecting it against an hour-long expected duration; and no network request under a provider hold. Existing caption parsing, persistence, recovery, search and localhost caption download tests pass. Synthetic fixtures are not evidence of successful live audio transcription.

The selector was also checked against actual saved metadata for qqzXl4z-m1M: it selected format 140-19, en-US, English (US) original (default), m4a. Format IDs are selected from metadata, not hardcoded.

Earlier real transfer for that recording returned a 195-byte HTML Site Unavailable response, despite the downloader reporting 100 percent. This is not usable audio and is not a successful transcript. The response alone does not identify the upstream party responsible. No new real audio transcription was achieved in this checkpoint. Windows end-to-end audio download, model execution and quality sampling remain untested.

The separately recovered private library remains 41 saved caption imports requiring review, 41 unresolved tested recordings and 1,212 untested recordings. No claim of all 1,294 sources being accessible or complete spoken Scripture coverage.

## Next validation before distributing a new cumulative release

Add real downloader localhost audio integration, cache recovery and timeout tests; surface audio diagnostics in the Access report; improve prompt cancellation and automatic batch continuation; run Windows CI and a genuine original-English lesson through download, ASR, reopening and search. Preserve Build 012 as the current packaged release until that validation is complete. No new package is designated ready by this checkpoint.
