# Build 012: deeper source-access investigation

Research and implementation date: 2026-10-22. Continues Build 011; no catalog or Bible reader changes.

## Findings and confidence

The owner-PC report contains 18 unique recording results: 17 caption imports saved for quality review and HTTP 429 while downloading `en` for `zzzw90JxgIU`. Build 010 requested both `en` and `en-orig`; Build 011 retained only `en`. Earlier attribution solely to speed was too strong. A one-hour wait was our client policy, not a server promise of unblocking.

The yt-dlp maintainers document a particular 429 problem with automatically translated captions. September 2026 reports specifically describe plain `en` failing while `en-orig` succeeds. This is a strong lead matching our error, not proof that this owner's failing request was translated: the supplied diagnostics do not include its caption URL. Other 429 causes remain possible.

Source inspection of the installed pinned yt-dlp 2026.10.21 confirms that original tracks and language aliases can coexist, and translation requests use a `tlang` URL parameter. Language labels alone are insufficient. A blanket switch to `en-orig` would also miss authored English and some native variants.

The implemented worker selects exactly one native English VTT, authored first and original automatic next. It excludes all URLs with a `tlang` parameter, even if labeled original, and records generation provenance. Translations are not needed for these English teachings. This is ordinary track selection, not a block bypass. No cookies, proxies or account switching were added.

## Implementation and verification

- Dedicated `caption_worker.py` uses the pinned yt-dlp Python API. Selection occurs from the metadata obtained for the current recording; no extra per-language probing pass.
- Skip translated-subtitle enumeration and HLS/DASH manifests. Add two-second extraction-request spacing and five-second subtitle spacing. Keep persistent 60-second inter-lesson spacing and all existing cooldown/block ceilings.
- Worker timeout increased to 120 seconds to accommodate internal waits. Pause can wait for the current subprocess to finish or time out.
- Saved records with attached sources remain skipped. For an unfinished attempt, refreshed metadata and selected captions replace only that attempt's download artifacts. Import requires the selected current track, not a stale matching filename.
- Full private metadata is retained using `--no-clean-info-json`: an integration test caught that yt-dlp's default metadata cleaning drops `requested_subtitles`. This metadata stays in the private library.
- Migration bookkeeping no longer consumes a network retry. Access report distinguishes unique recordings from network attempts.
- 35 automated tests passed locally with the pinned yt-dlp installed. Includes selection, stale-file rejection, migration/retry limits, parsing, persistence, recovery, search and existing catalog tests.
- Integration test runs real yt-dlp selection, HTTP VTT download and JSON writing against localhost with synthetic video metadata. It confirms exactly one native-caption HTTP request, zero translated requests and zero video downloads. This is explicitly not a YouTube access test.
- Existing cooldowns are preserved, including a reached three-event stop. No new successful owner-PC or live YouTube retrieval is claimed for Build 012. Windows execution of this new worker remains pending.

## How to reach the entire collection

1. After the saved cooldown, validate the new native-track selection against the failed recording on the existing Windows installation. Start / Resume handles this automatically if the existing retry ceiling has not been reached. Compare actual saved-file results, not merely process exit status.
2. If that succeeds, continue sequentially across the existing catalog, persisting results. No user supervision of individual lessons is required. If another hard block or the rate-limit ceiling occurs, stop rather than silently skip.
3. Separate genuine missing-native-caption cases from network failures. Missing-caption cases require accessible matching audio; local faster-whisper supplies recognition without per-video charges.
4. Official published audio is a rolling five-day archive, not a demonstrated complete back catalog. The two matching Genesis passage titles are source candidates, not proof of exact recording identity or access to all 1,294. Capture only published authorized links; do not enumerate file numbers.
5. The scalable fallback remains a ministry-provided archive manifest or matching local CD/DVD/audio collection. Import the whole directory/manifest, match exact catalog identities, and transcribe unattended. No external request has been sent.
6. Independently audit all 1,294 recording identities and the 31,102-verse dataset. Captions from every catalog video would not by itself settle disputed passage mappings or prove every verse was taught.

At the current minimum 60-second inter-lesson gap, the 1,277 recordings remaining after 17 saves require about 21.3 hours of pacing alone, plus request/import time and any cooldowns. This is a planning lower bound assuming access and native captions for every remaining recording, not a completion estimate. ASR time depends on accessible audio duration and actual Windows hardware. With a hypothetical 1,294 hours at 64 kbps, compressed audio alone is approximately 37.3 GB decimal; temporary decoding, models and backups are additional. No newly unavoidable paid service cost was identified.

## Paid services and missing dependencies

Supadata publicly documents native-first transcription with an AI fallback, timestamped chunks and asynchronous job results. That architecture can be reproduced with our persistent queue and local recognizer; its proprietary upstream access is not established by those docs. AssemblyAI requires a downloadable audio/video file URL or uploaded file; a YouTube watch URL is not itself usable audio. Paying for recognition does not by itself supply the missing recordings.

yt-dlp also documents a JavaScript runtime/EJS requirement for full YouTube support. The owner's logs warned about no runtime, but 17 captions succeeded despite that. It is a separate compatibility concern, not evidence that installing a runtime resolves this 429. Build 012 does not silently install new executable runtimes. Investigate that dependency if metadata extraction, rather than subtitle transfer, fails.

## Primary sources consulted

- https://github.com/yt-dlp/yt-dlp/issues/13831 — maintainer pinned explanation and September 2026 original-track reports; the scope is this specific issue, not all HTTP 429 responses.
- https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/youtube/_video.py — caption language, original-track and translation URL construction. Local pinned version inspected as well.
- https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py — selection and private metadata behavior, verified against installed pinned version.
- https://github.com/yt-dlp/yt-dlp/blob/master/README.md — separate request/subtitle sleep controls and extractor skip options.
- https://github.com/yt-dlp/yt-dlp/wiki/EJS — runtime/dependency compatibility.
- https://shepherdschapel.com/audio — current published MP3 listings.
- https://shepherdschapel.com/how-to-recieve — explicit rolling five-day audio archive description.
- https://shepherdschapel.com/video — current ministry book/video listings; not a complete direct-file manifest.
- https://docs.supadata.ai/api-reference/endpoint/transcript/transcript — native/generate/auto modes and asynchronous result handling.
- https://www.assemblyai.com/docs/faq/how-can-i-transcribe-youtube-videos — watch URLs not accepted as direct audio.
- https://www.assemblyai.com/docs/faq/what-types-of-audio-urls-can-i-use-with-the-api — downloadable file or upload requirement.
- https://github.com/SYSTRAN/faster-whisper — local recognition implementation already used by the app.

No full collection access, transcript accuracy certification or complete Scripture teaching coverage is claimed.
