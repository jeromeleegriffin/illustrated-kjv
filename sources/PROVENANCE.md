# Data provenance

## Authorized KJV scripture

The existing dataset remains unchanged at verse level. It derives from `thiagobodruk/bible`, `json/en_kjv.json`, whose original downloaded bytes hash to `fc99486e7d3b86e4ad1f0f424b36ab41b4ec4db858a776bd13aee1b7910f136b`. The app's canonical 66-book text is retained in `dist/bible.json`.

## Bullinger Companion Bible notes

Original work: E. W. Bullinger's Companion Bible (1909–1922), completed after his death. Public-domain historical work. Downloaded from https://www.sermonindex.net/modules/mybible/SI-CBNOTES.commentaries.zip. The source module's metadata explicitly says public domain and prepared by SermonIndex.net; the retained listing says “Free to copy and pass on.” The module was published September 27, 2026. The older July 2026 report that no redistributable module was found predates this source release.

`dist/bullinger/manifest.json` records source digest, all counts, metadata, and the 12 reference exceptions. All 23,934 rows are imported. Original transcribed words are preserved as plain text paragraphs; application links are added to appendix references.

## Bullinger appendices

Original historical appendix studies, maps and tables: https://www.levendwater.org/companion/index_companion.html. All 198 numbered appendix pages are locally included, plus 179A and the linked Appendix 50 section VIII. Original diagrams were downloaded from URLs explicitly present in those pages. The site's navigation, scripts, proprietary CSS and presentation attributes are removed; the app supplies its own plum styling. Original-source links are retained for comparison. Raw source pages are retained for audit/reproduction.

The separately researched PDF had incomplete appendix coverage and is not used as the app's appendix source. It is not part of the deliverable.

## Strong's alignment and dictionaries

KJV word alignment: https://ebible.org/Scriptures/eng-kjv2006_usfx.zip. The provider identifies this edition as King James (Authorized) Version, standardized 1769 text with Strong's numbers, courtesy of eBible and CrossWire. Its source copyright notice is retained. Only corresponding word tags are transferred; the scripture wording is not replaced. Unmatched source words are recorded and not guessed.

Strong's dictionary digitization: https://github.com/openscriptures/strongs. Strong's original historical dictionaries are public domain. The retained JSON-source headers identify the digitization as Copyright 2009/2010 Open Scriptures, CC-BY-SA, with attribution to Ulrik Petersen (Greek), David Instone-Brewer and David Troidl (Hebrew). The app's dictionary JSON files adapt the field names without replacing definitions. Attribution and the original license notices travel with the files; the adapted dictionary data is distributed under the same CC-BY-SA terms stated by its sources.

## Other retained content

Original 5,000-question bank, trivia gameplay, browser progress behavior, vector illustrations and 123 Genesis editorial study notes are preserved. The editorial notes are not attributed to Bullinger. Verification compares the full original trivia question objects and every KJV verse with their existing sources.
