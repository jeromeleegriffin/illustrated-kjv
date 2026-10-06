# Project brain

The product is a clean Authorized King James reader. Study tools stay available without replacing scripture. Trivia is a secondary link, not the home screen.

Architecture is a static site in `dist/`: `index.html` is the reader, `bible.html` keeps prior deep links, `app.js` renders the chapter, `reading.js` stores progress, and `search.js` handles references and text search. No new backend was added.

Bible text is the existing 1769 public-domain KJV dataset, 31,102 verses, source SHA-256 `fc99486e7d3b86e4ad1f0f424b36ab41b4ec4db858a776bd13aee1b7910f136b`. Do not modernize or paraphrase it.

Strong’s alignment comes from the eBible/CrossWire KJV word tags. Definitions come from the Open Scriptures Strong’s lexicon, CC-BY-SA, stored under `dist/strongs/`. Hebrew/Aramaic ids start with H; Greek ids start with G. Links are blue and underlined as buttons.

Bullinger notes are the SermonIndex Companion Bible Notes module, identified by that provider as public domain, stored under `dist/bullinger/`. Links are yellow/gold and separate from scripture. Do not present them as Bible text.

Reading progress uses `localStorage` key `illustrated-kjv-reading-v1`: a bookmark `{book, chapter, verse}` and read-verse ids `book:chapter:verse`. Selecting a verse marks it read. Mark unread removes only that verse. Do not clear storage to fix bugs.

UI rules: scripture dominates; Strong’s is blue; Bullinger is yellow/gold; both have a second cue (button treatment, not color alone). Genesis contextual notes stay labeled as study notes.
