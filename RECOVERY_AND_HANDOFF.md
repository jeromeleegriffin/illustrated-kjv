# Recovery record and Grok handoff

## Recovered state

The prior local download `002.zip` was successfully built and saved. The prior source workflow also completed for commit `ac3b72a0ab505554efbdc4287ecafaa94700d348`. The visible response then stopped during its save-and-publish call. Read-only recovery found Site version 3 and confirmed that the prior publication eventually succeeded. That prior version contains externally hosted Bullinger note access, not this revision's local note/appendix integration.

The existing project and the standalone 5,000-question trivia game were preserved. This revision was developed locally, without new pushes or deployments.

## Faults repaired

1. The `.search-backdrop` and `.modal-backdrop` author CSS specified `display:grid`, overriding the browser's default styling for the `hidden` attribute. This caused dialogs to appear on entry. Explicit `[hidden]{display:none!important}` repairs their visibility.
2. The phone stylesheet hid the only search control. A header search button is now visible on both phone and desktop layouts.
3. Invalid references could navigate to nonexistent chapters and throw during rendering. Reference search now validates the actual chapter and verse bounds and explains the valid range.
4. Root-absolute asset and JSON URLs failed when the app was hosted under a project subfolder. Runtime paths are now relative.
5. The old Strong's API endpoint returned HTTP 404. Word tags and dictionary entries are now bundled locally from identified sources.
6. The study reader was not linked to the existing trivia app. The original trivia app is now the default entry, with clear Bible/Search/Appendix controls; answer citations open the in-app Bible.
7. The earlier Bullinger reader depended on a third-party iframe. The imported notes are now displayed as local, attributed study content beside relevant KJV verses.

## Review before Grok publishes

Use the full `dist/` tree as the static app. `index.html` is now the Bible entry, `trivia.html` the trivia page, `bible.html` a compatible scripture reader, and `appendices.html` the appendix reader. The hosting provider/repository choice remains for Grok and the owner. No GitHub account, repository, or branch has been invented for this handoff.

Keep the existing trivia storage key so prior progress resumes when the app is served under the same origin. All dictionary/appendix provenance and coverage exceptions are retained in the included manifests. Review `verification/` for the actual outcomes; do not treat a successful import alone as a browser verification.

## Later owner correction — revision 004

Jerome clarified that the Bible is the main entry and trivia belongs behind a link. This supersedes the trivia-first decision in the recovered revision. Strong references are blue and Bullinger links are yellow. Persistent reading progress and an explicit verse bookmark were added with a Bible-wide expandable overview. The data integrity check remains PASS; new bookmark, storage, color and tracker behavior passed on desktop and phone. This revision remains local and unpublished for Grok.

## Revision 005 — repeated search-first report and font controls

Local inspection found the remaining `?search=1` auto-open branch. Removed it, added an entry/restoration search-close rule and embedded hidden-state guard, and versioned reader asset URLs. Added saved A− / A+ reading controls. Owner-reported live behavior was not independently inspected because no current URL was supplied; an older publication will remain older until Grok publishes this revision. No pushes or deployments were performed. See entry-font-report.json for this revision’s actual verification result.
