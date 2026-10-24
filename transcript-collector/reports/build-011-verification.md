# Build 011 verification — 2026-10-22

## Real owner-PC evidence
Uploaded Build 010 youtube-source-report.json: 18 unique attempts, 17 saved_quality_review results, then zzzw90JxgIU subtitle download returned HTTP 429 Too Many Requests. Successful logs request both en and en-orig. Requests were seconds apart. No claim that missing JavaScript runtime warnings caused this HTTP 429. No claim of listening accuracy or full collection access. Private raw diagnostics and captions are excluded from GitHub.

## Changes and validation
26 local unit/integration tests pass, including persisted cooldown across reopening SQLite, no network during a paused legacy-429 migration, 60-second spacing across separate runs, single-track command selection, and a three-event retry ceiling. Existing 403 hold remains permanent. Timing tests use injected clocks and synthetic responses; these are not evidence of successful live recovery. Existing genuine Windows retrieval evidence pertains to Build 010 only.

The default cooldown is 3600 seconds, doubled on subsequent rate-limit events. No Retry-After header is available from this subprocess log. Generic rate limits can recur despite pacing. No cookies/proxies or authentication/captcha bypass are added. Requests stop after three rate-limit events across sessions, not three per restart.

## Remaining limits
Build 011 real Windows access after cooldown remains untested. Caption accuracy/completeness and full catalog availability remain unproven. This release requests exact en only; variant-only captions remain unresolved, not marked complete. Saved transcripts retain catalog teacher labels with independent review pending. No production reader/catalog changes.
