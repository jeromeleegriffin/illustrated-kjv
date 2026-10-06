# Current status

Revision 005. Bible-first reader with search-entry repair and saved font controls. Integrated from candidate 005.zip SHA-256 ae7ba19d1650757f336903bda3abf10fe6a314d17e4254297d1c56628d6a0c59. Outer handoff Bible_1.zip SHA-256 d911af354df446dfbb9439672bec16a4ae80a6c02ea7c3fb58b7c14c332638ac; the inner archive hash matched.

Repository: https://github.com/jeromeleegriffin/illustrated-kjv
Branch: main
Archive commit: f8940a71356933b8393d083befa08b252c009c71
Publish branch: gh-pages commit f6ce74c8c3e6b86252d87a2cf160a0fea0a13135
Publish directory: GitHub Pages is configured to serve gh-pages at /. dist/ was copied to that branch root, not nested.
Public URL: https://jeromeleegriffin.github.io/illustrated-kjv/

Before this integration: main 9e805e9a7e6e61a9c0ab2ee8e6375111cc76110f, gh-pages b03f27fc06553f9db81cb20e0fb279ba7e968126.

Local HTTP checks passed on 2026-10-06: verify_data.py, verify_app.cjs, verify_reading.cjs, verify_entry_font.cjs against http://127.0.0.1:8767/.

Public Pages has not rebuilt. Last Pages build is 2026-10-06T12:26:55Z commit 2fe25540919e9671b4abf00aa6d29f1447a0aadf. A rebuild request returned 403. The live URL still does not show Revision 005.

Completed in 005: full 66-book KJV reader (1,189 chapters, 31,102 verses), search only on click including old ?search=1 URLs, local Strong’s links, local Bullinger notes and appendices, verse highlight, bookmark, read/unread progress, font size 16–32 px default 20, secondary trivia link.

Incomplete: eight Bullinger records have unresolved verse numbers and four Psalm title notes stay at chapter level. Printed introductions and every structural diagram are not certified against scans. 110 tagged tokens were not guessed.

Browser data stays local to origin. illustrated-kjv-reading-v1 and illustrated-kjv-font-size-v1 are not synced across domains.


Recheck 2026-10-06 21:09 UTC: the later Bible-first instruction was compared with revision 005. No runtime files were changed. verify_data.py, verify_entry_font.cjs, verify_reading.cjs, and verify_app.cjs passed again on http://127.0.0.1:8767/. Public Pages rebuild still returns 403. Live URL still serves the 12:26 build, commit 2fe25540919e9671b4abf00aa6d29f1447a0aadf.
