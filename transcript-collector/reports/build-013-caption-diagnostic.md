# Build 013 development: stage-specific caption diagnostic

Continues the existing isolated collector. Production Bible reader and catalog unchanged.

## Confirmed live result

On October 23, 2026 (America/New_York), the actual caption_worker.py, with yt-dlp 2026.10.21 and Python 3.12.14 on Linux, downloaded qqzXl4z-m1M (Genesis 27:30–28:19, Arnold Murray). Discovery and native authored-English selection completed. VTT parsed to 1,133 cues, starting at 2.268 seconds and ending at 3505.735 seconds. Parsed segments were saved and reopened. VTT SHA-256: 5e4b9330300180e1872dfc3f8403ee51268b5a7619405dddabb1f7cbb789a1db.

Comparison with the user's previously imported transcript yielded 8,182 normalized alphanumeric tokens in each, SequenceMatcher ratio 0.9998777804937669. This is agreement between two text sources, NOT audio accuracy measurement. The recording was already in the private 68-recording library and is not counted again.

No authentication, proxy rotation, token bypass, GetTheText scraping or audio download was used. This establishes one real caption retrieval, not full collection access or a proven explanation of prior failures. Earlier Work browser-export failures must not be attributed to this worker without evidence.

## Implementation

- caption_worker.py emits an optional allowlisted stage record through GRIFFIN_CAPTION_DIAGNOSTIC. No caption URLs, request headers or tokens enter this record.
- diagnostic_captions.py invokes that actual worker using fresh extraction, a new output folder per run, finite timeout, zero extractor/download retries, and one native English track. Default one known recording; explicit count up to three. Stops after any failure; 60 seconds between successful requests.
- Raw subprocess output remains in memory solely for coarse error classification; it is not saved to the shareable report.
- Separately reports discovery, selection, file receipt, parsing and saved/reopened segments. File existence alone cannot produce success; HTML and partial files from nonzero processes fail.
- CHECK_CAPTIONS.bat uses the existing installed environment. Close the collector before running, and do not run during an active cooldown. This standalone tool does not consult the user's database/cooldown and must not be used as a retry loop.
- Diagnostics contain private caption files; share report.json only. No changes to the teaching library.

## Validation and limits

44 automated tests pass with yt-dlp and PyAV dependencies installed, including five new diagnostic tests and a localhost transfer integration test. Windows execution remains unverified. The diagnostic has no second-provider implementation yet; it deliberately does not incorporate Grok's obsolete API call or unsafe URL redaction.

Grok's suggested experiment was useful, but its script bypassed the custom selector, only checked file existence, did not implement block stopping and replaced the string http without removing sensitive URL parameters. Those issues are not carried into this diagnostic.

The latest private collection has 68 unique imported transcripts, all quality review, zero verified complete. Full 1,294-recording access, independent audio accuracy, and comprehensive spoken verse coverage remain unproven. Audio fallback remains an opt-in development feature. No new packaged Windows release is implied by this checkpoint.

## Follow-up after environment recovery

HcWbNez6GUY (Genesis 41:1–41:49, Arnold Murray) also succeeded: 1,087 cues, 2.202 to 3505.335 seconds. SHA-256 6288551409923ef06b1437c9bff0d229fb03ce720ed50c92d839bf58f245556f. All 7,991 normalized alphanumeric text tokens match the user-supplied SRT export. This is cross-export agreement, not independent audio review. The interrupted follow-up had no saved result; only this resumed run is counted.

NV99i2jcIJU (Ezra 1:1–2:2, Dennis Murray) succeeded: 1,014 cues, 0.6 to 3506.402 seconds. SHA-256 b15856c2eb42eb9037efe1e5bdfef12aa550272233864f9a578ddc13bbe4ab32. Normalized caption text matches the user SRT: True. Three confirmed live retrievals now cover both pastors. No additional unique library recordings were added.
