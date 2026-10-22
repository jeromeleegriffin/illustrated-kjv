# Griffin Shepherd's Chapel Transcript Collector — Build 010

**Engineering release, not a completed Bible teaching archive.** Continues recovered Build 007 and the existing transcript branch. The Bible reader is unchanged. No paid transcription API is used.

## Windows start

1. Extract the entire ZIP to a writable folder. Do not run inside the ZIP.
2. Double-click **START_HERE.bat**. Python 3.12 (64-bit, with Tcl/Tk) is required. If absent, the launcher opens the official Python download page and explains what to install. No programming is required.
3. First launch creates an isolated `.venv` and installs free dependencies. Internet is needed for installation and the first model download. After installation and model caching, local transcription works offline.
4. The desktop opens the bundled catalog automatically. The default private data folder is `GriffinShepherdLibrary` in your Windows user folder. Settings can open a different library; it does not move or delete an existing one.
5. Import authorized files with **Import Folder**, or select a recording and use **Attach File**. Filenames should include the exact 11-character catalog video ID, e.g. `Genesis [J2Ia_1jDRdc].mp3`. A `.metadata.json` sidecar can supply `{"video_id":"J2Ia_1jDRdc","teacher":"Arnold Murray"}`. Ambiguous files are reported, never guessed.
6. For unattended bulk access, use **Import approved source manifest** after the ministry supplies a verified file/URL mapping. See `SOURCE_MANIFEST_EXAMPLE.json`. Then **Start / Resume** processes all ready sources sequentially.
7. Search by word, phrase words, teacher or Scripture reference. Search combines words using AND and returns up to 200 timestamped segments. Topic discovery is lexical, not an invented theological interpretation.

**The software does not currently obtain all catalog recordings automatically.** This depends on obtaining a permitted, identity-verified archive manifest. Scanning official listings produces candidates, not automatic approval or fabricated source availability. The two published matching Genesis titles do not prove access to all 1,294 recordings.

## Controls and data

- Start / Resume: collect captions through the configured permitted provider, then process ready local sources, preserving committed chunks.
- Pause / Stop: stop after the current five-minute chunk. Closing waits for a safe checkpoint. Forced termination can lose the current chunk only; resume reprocesses it.
- Retry Failed: explicitly retries eligible attached failures, maximum three processing attempts. Access-blocked sources are not retried automatically.
- Verify Library: checks saved checksums, attribution and timestamp bounds. Structural validity does **not** certify recognition accuracy or entire-recording coverage.
- Scan official listings: read only links actually published on the audio page. No endpoint enumeration.
- Online Source: explicit authorized direct media URL for the selected lesson. Watch-page extraction is not supported. Online downloads default OFF.
- Settings: model, CPU/CUDA, data directory, disk reserve and maximum download size.

`library.sqlite` is the durable catalog, status, segment checkpoint and FTS5 search database. `transcripts/ID.json` is the readable timestamped export. `hardware.json`, `verification.json`, `import-report.json` and `source-import-report.json` explain diagnostics. Keep the entire private data folder backed up **while the app is closed**. Do not put it in a public Git repository. SQLite WAL/SHM files belong with a live database; copying only the database during processing is not a safe backup.

## Recognition

Default: `small.en`, CPU int8, up to four CPU threads. Approximate first-download model sizes: base.en 150 MB, small.en 500 MB, medium.en 1.6 GB. Dependency installation and caches need additional space. Hardware detection is saved automatically; CPU is the conservative default. CUDA selection requires compatible NVIDIA CUDA/cuDNN libraries; a detected GPU is not an inference guarantee.

The engine uses faster-whisper with streaming PyAV decoding. Fixed five-minute chunks have transactional checkpoints. Chunk boundaries, empty recognition, low confidence, compression repetition signals and repeated adjacent lines create review warnings. Distinct spoken repetitions are retained; overlapping identical caption cues are merged. Limited Bible-name hints are recognition prompts, not substitutions for speech. No LLM rewrites or fills text. Full accuracy, punctuation, Greek/Hebrew spelling and cross-boundary word recovery are **not guaranteed**.

Every generated transcript enters `quality_review`. There is deliberately no automatic path from “recognizer finished” to “verified complete.” Caption-only imports infer duration from the final cue and cannot establish recording completeness without the original media. Human/audio verification and exact source identity reconciliation remain necessary for certified completion.

## Verification and limits

See `reports/`, `FEASIBILITY_AND_HANDOFF.md`, and GitHub checks. Automated fixtures are synthetic and not presented as ministry transcripts. Full audio/transcript pilot output is kept private and is not bundled or committed. The Windows launcher is source-based, not a signed portable executable. A Windows CI smoke test exercises the desktop; it is not a substitute for testing the owner's hardware.

The original Build 007 code/tests are preserved under `legacy007/` for recovery only. Their old network collector is not invoked by this app. The current workflow performs offline tests and does not repeatedly probe blocked YouTube URLs, publish transcripts, or deploy the Bible reader.

Windows installation validation passed in GitHub Actions run 39730444804: dependencies installed, base.en CPU model loaded and inferred on synthetic silence, desktop opened. Full real lesson inference was tested on Linux; accuracy and owner-PC performance remain unverified.

## Recover a damaged caption library

Close the collector. Keep the damaged directory unchanged. From the installed collector directory, use its Python environment:

```bat
.venv\Scripts\python.exe recover_captions.py --catalog ..\dist\bible-teaching.json --source "C:\Study\caption-sources" --destination "C:\Study\RecoveredLibrary"
```

The destination must not exist. This offline command copies preserved browser `.txt` caption exports, checks source hashes, builds a fresh database, reopens it and checks SQLite integrity/search. It writes `recovery-report.json`; rejected files are listed and never counted as saved. After success, choose the recovered directory in Settings. It restores captions only, not audio processing checkpoints, settings or previous review decisions. Transcripts still require accuracy/completeness review. Keep both the original and recovered directories until you have inspected the result.

## Experimental permitted YouTube captions

Build 010 includes a caption-only provider and a five-recording access test. It requires enabled online sources, a permission basis, and the updated requirements (`yt-dlp==2026.10.21`). Existing installations must install the updated requirements before using it. It never downloads the video/audio, imports cookies or bypasses platform controls. A block pauses this provider persistently; `Retry Failed` does not clear that hold. Read `youtube-source-report.json` in your private output directory for the exact error. Saved captions remain quality_review. A clean downloader exit without a valid saved caption is not success.

The real cloud probe was blocked by YouTube; successful standalone Windows acquisition is NOT established. Do not use this as a claim of complete archive access.

## Build 010 pre-install improvements

The Access report button explains results without exposing transcript contents. English captions tagged en, en-orig, en-US or en-GB are supported. Windows downloader diagnostics use explicit UTF-8 decoding. Numeric video titles do not trigger false HTTP blocks. Transient/dependency failures can be retried by explicitly starting again, up to three attempts per recording; blocked access still holds the provider. If setup fails, read setup.log; REPAIR_SETUP.bat reinstalls dependencies without deleting your study library. Build 010 replaces Build 009.
