# Authorized KJV Bible Trivia & Study App

Continue the existing project. The starting page is the full Authorized King James Version reader, with the original 5,000-question trivia game available through its Bible Trivia link. Search opens only from an explicit in-app control.

## Run locally

From this project folder on Windows:

```text
py -m http.server 8087 --bind 127.0.0.1 --directory dist
```

Open http://localhost:8087. On systems with `python3`, use `python3` instead of `py`. The JSON data files require an HTTP server; opening the HTML directly as a `file://` URL is unsupported. Port 8087 avoids the other existing port-8000 project.

## App sections

- `dist/index.html`: Bible-first entry. `dist/bible.html` preserves prior reader deep links.
- `dist/trivia.html`: original trivia app; all 5,000 questions and its existing browser progress key are preserved.
- `dist/bible.html`: illustrated Authorized KJV reader. Its header has a visible **Search the Bible** button on phones and desktops. It supports word/phrase search, book names, chapter references, full verse references, common book abbreviations, and validation of invalid chapter/verse numbers.
- Plum **B** markers beside verses open the imported Bullinger notes in a separately styled study panel. The chapter button shows all imported notes for that chapter.
- `dist/appendices.html`: all 198 numbered Companion Bible appendices, plus Appendix 179A and Appendix 50 section VIII, with original tables and 49 local image assets. Appendix references inside notes link into this reader.
- Strong's linked words use locally stored KJV word alignment and dictionaries. Direct BibleHub links remain available for independent comparison.

## Text and source integrity

The scripture layer preserves all 31,102 verses of the existing 66-book KJV dataset. No scripture word has been replaced with Bullinger's proposed renderings or a generated contextual paraphrase. The original source file's SHA-256 is `fc99486e7d3b86e4ad1f0f424b36ab41b4ec4db858a776bd13aee1b7910f136b`.

- KJV scripture source: https://github.com/thiagobodruk/bible/blob/master/json/en_kjv.json
- KJV word tags: eBible/CrossWire's King James (Authorized) Version, identified as standardized 1769 text: https://ebible.org/find/show.php?id=eng-kjv2006
- Bullinger notes: 23,934 records from SermonIndex's **The Companion Bible Notes** module. The provider explicitly identifies its module downloads as public domain and free to copy and pass on: https://www.sermonindex.net/modules/
- Bullinger appendices: original public-domain studies transcribed at https://www.levendwater.org/companion/index_companion.html. Source presentation has been adapted to this app's separate study design with yellow links; comparison links are retained.
- Strong's dictionary digitization: Open Scriptures, https://github.com/openscriptures/strongs. Original dictionary works by James Strong; the digitization is marked **CC-BY-SA** in the retained source headers. Attribution and those headers are included in `sources/`.
- Genesis context draft: 123 earlier editorial notes, retained and labeled as contextual suggestions rather than Bullinger's words.
- Illustrations in the scripture reader: original vector scenes already in the app.

## Coverage and limits

All 23,934 records in the named Bullinger module are retained. Four Psalm title notes use verse 0; eight records have source verse numbers outside the corresponding KJV chapter. Those records are retained at chapter level, labeled for review, and never assigned to invented verses. This is a complete import of the specified note module and the 198 numbered appendix pages; it is not certification that every printed book introduction or structural diagram in every Companion Bible edition has been transcribed.

Strong's tags are mapped to the existing KJV word tokens without altering verse text: 361,947 linked tokens across all 31,102 verses, with 14,197 dictionary records. 110 tagged tokens in the source could not safely be mapped to the existing verse text; unmatched source tokens are not used to invent word attachments. The manifests record the source comparison details.

The 5,000-question bank is unchanged. Its earlier human editorial-review limitation remains. Contextual reading suggestions remain study interpretations for comparison.

## Verification and handoff

The `verification/` folder contains the data checks, browser report, and actual desktop/mobile screenshots. Source import scripts are in `scripts/`. All public runtime assets are in `dist/` and use relative paths for a hosted subfolder such as a GitHub Pages project path.

This recovery revision is a local downloadable handoff for Grok. No GitHub push or deployment was performed for this revision. Do not include `sources/` or `verification/` as public runtime assets unless intentionally desired; they are for provenance and review.

## Reading controls — revision 004

Strong’s word references are blue; compact Bullinger B links are yellow. Commentary remains a separate panel. Click or keyboard-activate a verse to highlight it and mark it read. “Bookmark this verse” saves the selected verse (or the first verse of the current chapter when none is selected there); “Go to bookmark” returns to it. The saved bookmark restores when the app opens.

“Entire Bible · Reading progress” opens all 66 books, with expandable chapters and verse buttons. Read verses are gray; counts show read and remaining verses. The main scripture keeps its ordinary typography and current highlight. “Mark selected verse unread” corrects accidental clicks. Navigation, search and opening a chapter alone do not mark it read.

The reading store uses `illustrated-kjv-reading-v1`, independent of the unchanged quiz storage. Progress and bookmarks persist in that browser on the same origin. They are not synchronized across devices. If browser storage is unavailable, an inline message explains the limitation. No scripture wording, question bank or imported commentary was changed. Actual desktop and mobile checks are recorded in `verification/reading-report.json`.

## Opening and text size — revision 005

Removed the legacy `?search=1` automatic opening action. Search remains available through the in-app buttons, but stays closed on entry, reload, and pageshow restoration. Both reader entry files embed a high-specificity hidden-state guard and use versioned CSS/JS URLs to avoid reuse of obsolete assets.

A− / A+ adjust the reading size from 16 to 32 px in 2 px steps. Clicking the size resets to 20 px. Scripture, linked words, and study-note text resize together; scripture remains unchanged. The independent setting `illustrated-kjv-font-size-v1` persists per browser. Existing bookmarks, reading progress and trivia keys are preserved.
