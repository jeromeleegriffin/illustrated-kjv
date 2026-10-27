Content-first Bible presentation, 2026-10-27 UTC

Applies a separately pinned CSS/JS presentation enhancement to reader, appendices, trivia, teaching choices, FAQ, topical studies, collection details and legacy bible.html. Existing Bible/FAQ/topical/reader pins, stored progress, catalogs and teaching content are preserved. Worker inserts styles and deferred enhancement after retrieving the existing asset; original cached HTML remains unchanged. Keep COMPACT_RELEASE, routing and HTMLRewriter when updating FAQ pins.

Appendices: compact title, optional explanation, collapsible mobile chooser, smaller document heading. Trivia: reduced header/round chrome, unchanged question bank. Teaching choices: optional instructions and compact filters. FAQ remains question-first with fixed navigation. Typography changes target chrome rather than scripture.

Syntax checks passed. Unrelated Worker settings are preserved through content-only upload. Rollback: remove the COMPACT injection or revert the Worker source to its previous version.
