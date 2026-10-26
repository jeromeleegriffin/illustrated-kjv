GRIFFIN SHEPHERD'S CHAPEL FAQ BATCH PROCESSOR — BUILD 001

This companion app processes the saved private caption library into timestamped FAQ
candidates. It preserves the existing approved FAQs and the Bible application.
It does not collect videos, transcribe audio or automatically publish AI answers.

WINDOWS INSTALLATION
1. Extract the entire ZIP into a normal folder (not inside the ZIP viewer).
2. Double-click START_HERE.bat or GriffinFAQProcessor.exe.
   Python is bundled. Do not install Python or run pip.
3. Your browser opens the private app on this computer. Keep the console open.
4. Select Griffin_Private_Teaching_Library_Batch_001.zip and click Import ZIP.
5. Click Set up free AI. The official Ollama Windows runtime downloads if needed
   (1.59 GB) and the local Qwen3 8B model downloads (about 5.2 GB).
   No payment or account is required. Read the linked model license before use.
6. Click Start / Resume. Leave Windows on and awake. CPU-only is supported.
7. Download private results ZIP when desired. Return it for FAQ reconciliation.
   Keep it private: it contains caption evidence, not just public paraphrases.

Windows 10 22H2 or newer, x64. Recommend at least 16 GB RAM and 14 GB free storage,
plus your private archive. Inference speed depends strongly on the computer.
The download happens once. Processing uses a local AI endpoint, never a paid API.

RECOVERY
Pause/Stop finishes the in-flight window then pauses. Closing the console or a
power loss can interrupt that window: reopening recovers it automatically; click
Resume. Previously saved windows are not repeated. Retry Failed is explicit.
Reimporting an unchanged archive skips existing sources. Changed source hashes
stale old jobs and create a fresh queue, retaining the old source privately.
Private data is stored in %LOCALAPPDATA%\GriffinFAQProcessor. Back up this folder.
Do not delete it when updating the program. No public registry is overwritten.

QUALITY AND LIMITS
Every recording is scanned in overlapping windows from its beginning to its end.
This avoids assuming Q&A always starts after minute 30. The AI may still miss a
question, mistake a rhetorical question for a listener, or paraphrase incorrectly.
Exact cue indices, timestamps, hashes and original caption evidence are retained.
Machine completion is NOT fully-reviewed status or audio verification. Cut answers
and paraphrases exceeding very thin selected evidence are withheld for repair. Teacher
identity from the catalog is not independent verification. Unconfirmed topical
teachers, known attribution holds and external reservations are held automatically.
Question-group merging, ranking and publication remain the existing review step.
Different answer variants must remain separate. No invented Bible corrections.

TROUBLESHOOTING
An error is shown in the page and diagnostics.log; engine.log records local AI
startup. A model/runtime error pauses the queue rather than failing every source.
Retry after fixing disk space or restarting the app. Never delete the database to
fix an error. If the browser is closed, launch the EXE again to reopen its page.
Windows may show an unsigned-app warning: this build is not code-signed. The
release source and automated Windows tests are available on the development PR.
Do not disable Windows security. If your system refuses it, report the exact text.

SOURCE / DEVELOPMENT
Repository jeromeleegriffin/illustrated-kjv, work/shepherd-transcript-collector.
Code: transcript-collector/faq/batch-app. Tests: python -m unittest discover -s tests.
Packaging is performed on Windows with PyInstaller 6.16.0. The official Ollama
runtime ZIP is pinned to v0.40.11 and checked against its release SHA-256 before
execution. Model download is performed by Ollama's verified model pull.
