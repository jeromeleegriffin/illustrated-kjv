# Shepherd’s Chapel FAQ review

Current approved registry: 1,393 question groups and 2,208 linked answer occurrences. Frequencies are lower bounds from reviewed passages, counted once per question per underlying recording group.

All 1,360 private exports have been scanned for candidates. Sixteen recordings have complete caption Q&A reviews, 175 remain partially reviewed, 1,104 await passage/supplement review and 65 topical exports await teacher confirmation. Scanning never approves answers. Caption review is not independent audio verification.

## Rebuild

Run `python3 transcript-collector/faq/update_faq.py --library PRIVATE_LIBRARY --dist dist --registry transcript-collector/faq/reviewed-occurrences.json`. Keep transcripts, media and candidate excerpts private. Commit only paraphrases, code and sanitized metadata.

Occurrences bind teacher, video, exact caption anchors and transcript hash. Changed hashes invalidate approval. Preserve answer variants and documented recording aliases. The `recording_reviews` array stores explicit Q&A boundaries, reviewed ranges, unresolved ranges and a resume cursor; only contiguous complete review with confirmed boundaries qualifies as fully reviewed. Never infer completion from occurrence presence.

## Validation and publication

Run tests under `transcript-collector/faq/tests`. Verify duplicate counting, distinct variants, resume, hash invalidation and completion evidence. Rebuild frequency ranking and source ledger from approved occurrences.

Publish only the six FAQ assets using the separate FAQ release pin on the existing Bible Worker. Read the current Worker and settings before changing that pin; preserve the Bible release and unrelated routes. Never merge main, deploy GitHub Pages or commit full transcript copies.

## External extraction assignments

Before selecting another new recording batch, inspect `external-review-assignments.json`. Set griffin-faq-grok-300-20261024-A has returned 300 result files with 4,641 question candidates in checkpoint 042. All hashes and caption anchors passed independent structural checks. Thirty-four result recordings have been semantically reviewed here (580 approved (including one locally recovered question) linked answers; twenty-eight candidates held; one rhetorical extension and one listener thanks excluded), one additional incomplete export is blocked, and 265 result recordings await semantic review. These results are reserved for reconciliation, not blanket-approved. External completion claims never replace current reviewed statuses. Imported results must retain their source hashes, caption evidence, full-Q&A coverage and precise cursor; structural validation alone does not approve teaching paraphrases or confirm speakers.

## Attribution hold

Do not approve `4pmWjZmHK1o` under the saved Arnold attribution: its named introduction and listener address identify Dennis. The original source remains unchanged. See the sanitized pass028 report and private attribution-holds checkpoint before further review.

## Recovered private batch

The39-answer Dennis checkpoint libfile_3a9e3631e500819183ae10f3f780a8e2 has been reconciled idempotently with the current registry. Sources5EOrPMZ3ZTM and5FJ-a7O6PL8 have complete caption Q&A reviews, audio pending. Do not import or count those39 occurrences again.


## Second external assignment

Set `griffin-faq-grok-300-20261025-B` reserves another 300 previously unreviewed Arnold Murray passage exports, excluding assignment A, reviewed records, known alias groups and attribution holds. Package: `Griffin_Grok_FAQ_300_Recordings_002.zip`. All 300 remain pending; preparation is not a completed review and does not change published FAQ counts. The package supplies untouched transcripts, cue-indexed reading aids, the full prompt and tested structural validators. Actual presenter, source completeness and semantics still require review.


## Cross-recording difference

Pass039 flags a difference concerning spiritual activity attributed to restrained fallen angels: djw2r6xERR4 allows it, while dClenWFh8sM had denied it in an earlier answer. Keep both source-bound variants and the related dsxz1k0gvew distinction; do not harmonize them without further review. All remain audio-pending.

## Fixed FAQ navigation

Pass041 anchors both paging bars to the viewport, reserves space above and below the question, and retains the existing button nodes so focus survives paging. Page changes return the answer to its start. Question length and expanded answers no longer determine the button positions.

Pass042 adds seventeen caption-reviewed Arnold answers from e7IuSxcDxZE, retains two uncertain citation ranges, and preserves the v026 press-and-hold navigation. No audio verification is claimed.


Pass043 adds sixteen linked Arnold answers from e8gesclhsXI after reading the full caption Q&A section. Five unresolved ranges remain held, including two candidate answers. Audio is pending. Existing FAQ and topical navigation remain unchanged.

Pass044 reviews complete caption Q&A sections in eD_yKo--7XQ and eOmt2RLaHUQ, adds twenty-nine linked answers including an omitted listener contact question, and retains seven unresolved ranges. Both recordings remain partial and audio-pending. FAQ resume and top/bottom Bible-return links are preserved.

Pass045 reviews the full caption Q&A sections in eT3p198HLmA and eV35FK3Wa4o, adds thirty-one linked answers, holds the missing stock-dividend question and flags an unsupported medical detail supplied by the external extraction. Three ranges remain unresolved; neither recording is marked complete. Audio is pending. Reading-position memory and fixed hold navigation are preserved.

Pass046 adds forty-five linked answers after complete caption Q&A reads of eqRKIYbtKTU and eruuV5NuxoQ. It records an additional deferred Revelation 2:17 question without inventing an answer, preserves four unresolved ranges and retains source-specific qualifications. Both recordings remain partial, audio pending.

Pass047 adds forty-eight linked answers from full caption Q&A reads of esaS22IyyLM, etXX5Kj57zM and euTxqceUlR4. Deborah’s unread question remains held, and eight unresolved ranges retain arithmetic, damaged references, incomplete qualifications and calendar ambiguities. All three recordings remain partial, audio pending. Previous page controls and reading-position memory are unchanged.


Pass048 adds thirty-seven linked answers after complete caption Q&A reads of ewz9wZQjCQg and ezPMqVOO8SU. Five source-specific ambiguities remain held, including divine-knowledge wording, a glory-term lexical identification, and a prophetic army’s route. Both recordings remain partial and audio-pending.

Pass049 adds sixty-four linked answers from four complete caption Q&A reads. fAT6qDIM_r8 qualifies as a full caption-section review; f3_aywKN6Lk, fBPvp86RN9w and fDdaF11Yo00 retain seven unresolved ranges, including two unread listener questions. Audio verification remains pending. Existing page behavior is preserved.


Local app batch 002 adds forty-six caption-reviewed linked answers and twenty-three question groups after direct reads of the complete Q&A sections in WaqJ4p4NLFY (Arnold), -DI3jbEdDpM (Dennis) and F1e-_aBWB4c (Dennis). All three remain partial because source-specific reference, unread-letter, unanswered or incomplete-answer holds are preserved. Question variants remain separate and counted once per question per recording group. A difference in Dennis’s prayer-address qualifications is flagged for further review. Machine extraction is separate from these caption approvals; model candidates never approve themselves. Private checkpoint: libfile_fa436b11a950819199b084328523b67c. Audio remains unverified.

Local app batch 003 adds twenty-one caption-reviewed linked answers and fourteen question groups from -4I5t3EgO9o (Dennis) and 0aUiY5kK8F0 (Arnold). Both remain partial: a garbled pork-reference cue, the name of Mary’s father and the Arnold export’s mid-answer ending are held. The complete available Q&A captions were read directly; one commentary-only listener letter was excluded. Machine output remains separately unapproved. Windows app 1.0.4 improves incomplete-answer holds, malformed-JSON recovery, empty-queue counts and automatic Windows sleep handling, and withholds proposals lacking an explicit source question/request signal. Audio remains pending.
