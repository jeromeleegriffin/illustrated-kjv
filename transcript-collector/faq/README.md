# Shepherd’s Chapel FAQ review

Current approved registry: 3,827 question groups and 5,397 linked answer occurrences. Frequencies are lower bounds from reviewed passages, counted once per question per underlying recording group.

All 1,360 private exports have been scanned for candidates. Twenty recordings have complete caption Q&A reviews, 399 remain partially reviewed, 876 await passage/supplement review and 65 topical exports await teacher confirmation. Scanning never approves answers. Caption review is not independent audio verification.

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


Local app batches 004 and 005 reconcile all 197 prepared proposals from the 1.1.1 user export: twenty were covered by batch 004; batch 005 approves 153 additional source-bound paraphrases after direct caption-passage review; twenty-four are held, excluded or duplicate drafts. Batch 004 also recovered four answers outside the prepared subset. The overall totals are 1,550 groups and 2,385 linked answers. No additional full-recording completion or audio verification is claimed. Partial review ranges, attribution checks, corrections, duplicates and unresolved items are retained privately. The rest of the uploaded extraction/checking backlog is not approved by these batches. Prior pending Dennis review must be reconciled against these new links before reuse.



Local app batch 006 adds fourteen caption-reviewed Dennis answers after reconciling the earlier private review of -Se_hLyShno and reading the full Q&A sections of -atyYXhtw4I and -p2BC68Wbyc. All three recordings remain partial: one unanswered listener comment in -atyYXhtw4I, one unanswered request in -p2BC68Wbyc, and four previously documented unresolved ranges in -Se_hLyShno. Three earlier answer timestamp spans were extended to include their explanation. Audio remains unverified.



Local app batch 007 adds twenty-one caption-reviewed Dennis answers. It reconciles the earlier pending private review of -Se_hLyShno and directly reads full caption Q&A sections of -atyYXhtw4I, -p2BC68Wbyc, -ZOPXfruXiQ and 1HPYqWElfKM. All five sources stay partial with nine unresolved or unanswered ranges. Earlier source link spans were extended to include their supporting explanations. No audio verification or full recording completion is claimed.


## Local app batch 008

Reviewed saved caption Q&A sections from BEOF84Xy1ks and B9BQaj07GTE, adding 43 source-linked answer paraphrases. Four uncertain or unanswered ranges remain held; audio verification is pending. Counts are provisional while other recordings remain unreviewed.



## Local app batch 009

Reviewed the full saved caption Q&A in 1zXiZlhcLP0 and Be8R9plq548. Added 43 linked answers, including five attached to existing questions. Four unresolved ranges remain held. Caption reviews are not audio verification.



## Local app batch 010

Reviewed saved caption Q&A in CQZ7KZ7oLaI, added 19 linked answers and corrected one existing end timestamp. Four unanswered or uncertain ranges remain held; audio pending.



## Local app batch 011

Reviewed five saved caption Q&A sections (2jk52OkZGC0, 32qk2GyzKhQ, 1tbXpRlZbS0, 3CyXwiPxF9Y and 32tnNqefRvo). Added 93 linked answer paraphrases; nine uncertain or unanswered ranges remain held. Audio verification is pending.



## Local app batch 012

Reviewed saved caption Q&A sections from AsLV6-6H2_M, CEZz_kdevBk and AuS09aFrCLs. Added 46 linked answer paraphrases; eight uncertain or unanswered ranges remain held. Audio verification is pending.



## Local app batch 013

Reviewed saved caption Q&A sections from B0kOKqE0Eo8, 85MlNOuwfZ8 and 7c-bl5jbZu0. Added 47 linked answer paraphrases; four uncertain or unanswered ranges remain held. Audio verification is pending.



## Local app batch 014

Reviewed twelve complete saved caption Q&A sections, adding 203 source-linked answers, 169 new question entries and preserving distinct variants. All twelve remain partial with 34 unresolved ranges, including unanswered subquestions, caption errors and context holds. Audio verification remains pending. Repeated caption redraws were removed from the reading view only; original source bytes and hashes were retained.


## Local app batch 015

Reconciles the eleven pending Dennis drafts without duplication and adds 55 source-linked answers after reading four complete saved caption Q&A sections. Four recordings remain partial with 17 unanswered or uncertain ranges. Original source hashes and private evidence are retained; audio remains unverified. Prior progress and navigation are preserved.


## Local app batch 016

Adds 56 caption-reviewed linked answers and 44 question entries from four saved recordings. All four remain partially reviewed with 17 unresolved ranges; the explicitly deferred Matthew 25 question is not counted as answered. Testimony without a question is excluded. Speaker handoffs identify Dennis despite older Arnold program introductions on two recordings. Original captions and source evidence remain private, and audio verification is pending.


## Local app batch 017

Adds 206 caption-reviewed linked answers from complete reads of 16 saved Dennis Murray Q&A sections, including split listener subquestions. Sixteen equivalent prompts were attached to existing groups; 164 new question entries remain. All 16 sources remain partial with 67 unresolved ranges, including unread/deferred questions, uncertain citations and contextual holds. 3 testimony-only letters were excluded. Caption evidence, original hashes, teacher handoffs and exact resume ranges are saved privately. No audio verification is claimed. Existing approvals and navigation are preserved.

Local batch018 adds49 linked Dennis answers and32 question groups after four full caption Q&A section reads. All four remain partial because of unresolved ranges. Audio verification remains pending. Prior approved records and navigation are preserved.


## Local batch 019

Reviewed the complete saved caption Q&A sections of 14 additional Dennis Murray recordings, adding 207 linked answer passages and 175 question groups after semantic grouping. All 14 retain specific unresolved ranges and remain partial; audio verification is pending. Prior progress, external assignments and unrelated reader changes were preserved. Four Python tests and both navigation suites pass; source hashes and anchors match, with no invalid approvals.


## Local batch 020

Adds 206 linked answer passages and 154 question groups from complete saved-caption Q&A reads of 16 additional Dennis Murray recordings. One section is complete; 15 retain exact unresolved ranges. Caption review is not audio verification. Existing registry entries, reserved assignments, navigation and reader releases are preserved. Source hashes, timestamp anchors, ranking, persistence and both navigation suites pass.


## Local batch 021

Adds nine linked Dennis answers and seven question groups after a full saved-caption Q&A read of K29AYa7KZQc. Exact unresolved ranges remain held; no audio verification is claimed. Existing approvals and page navigation are preserved.


## Local batch 022

Adds 210 linked Dennis answers and 150 question groups from complete saved-caption Q&A reads of sixteen recordings. All sixteen retain exact unresolved ranges and remain partial; audio verification is pending. Ten equivalent prompts join existing groups. Two earlier ordinary-repentance answers were corrected from the unforgivable-sin group to their appropriate forgiveness groups, without changing their wording or source evidence. Source hashes, anchors, prior progress, duplicate screening, ranking and both navigation suites were checked.


## Local batch 023

Adds 202 linked Dennis answers and 143 question groups from full reads of fifteen new saved-caption Q&A sections. All fifteen remain partial with exact unresolved ranges; audio verification remains pending. Equivalent questions join existing groups while source-specific qualifications remain distinct. Duplicate screening excluded ORC7CdSDUCA, whose Q&A repeats HceinrSTP-s; it was not counted or approved again. Original source hashes, evidence and excluded-review recovery notes are saved privately. Four Python tests, both navigation suites, original-record preservation, source anchors and ranking checks pass.


## Local batch 024

Adds 201 linked Dennis answers and 132 question groups from full reads of fourteen saved-caption Q&A sections. All fourteen retain unresolved ranges and remain partial; audio verification remains pending. Sixty-nine equivalent question entries join existing or same-batch groups without collapsing answer variants. QOdZ2YoWSng ends before Q&A and remains pending. PgZ1gKICArs attribution follows the official passage catalog; its saved intro lacks a presenter handoff, so audio/presenter confirmation is pending. Source hashes, original caption anchors, duplicate screening and older registry preservation were checked. Four Python tests and both navigation suites pass.


## Local batch 025

Adds 209 linked Dennis answers and 140 question groups from full reads of seventeen saved-caption Q&A sections. All seventeen retain unresolved ranges and remain partial; audio verification is pending. Sixty-nine equivalent question entries join existing or same-batch groups while source-specific qualifications remain separate. UuBGAVSmNC4 contains interleaved lectures and is held out without new approvals. Original hashes, caption anchors, duplicate screening, ranking and older progress were checked. Four Python tests and both navigation suites pass.


## Local batch 026

Adds 303 linked Dennis answers and 224 question groups from complete reads of twenty-four additional saved-caption Q&A sections. These recordings retain held ranges and remain partial; audio verification is pending. Two additional exports repeat previously reviewed Q&A sections and their 37 candidate answers are privately preserved but excluded from new public approvals. A truncated export ends before Q&A. Prior progress, source hashes, caption anchors, frequency ordering, duplicate screening and recovery checks passed. Four Python tests and both navigation suites pass.


## Local batch 027

Adds 236 linked Dennis answers and 164 question groups from complete reads of seventeen additional saved-caption Q&A sections. One section has no unresolved ranges; sixteen remain partial because specific caption or contextual holds remain. All audio verification remains pending. Preserves original source hashes, exact anchors, private excerpt evidence and prior progress. Duplicate Q&A screening found no repeated section in this batch. Four Python recovery tests and both navigation suites pass; no invalid approvals. The requested target was 500; this checkpoint contains 236 actual new linked answers.


## Local batch 028

Adds 26 source-linked Dennis Murray answers and 16 question groups after full saved-caption Q&A reads of two recordings. Both retain unresolved ranges and remain partial. Original source hashes and exact caption evidence remain private; audio verification is pending. Previous records, external assignments, and reader routes are preserved.


## Local batch 029

Adds 25 source-linked Dennis Murray answers and 14 question groups after full saved-caption Q&A reads of two recordings. Both remain partial with eight held ranges. Original source hashes and evidence remain private; audio verification is pending. Prior records and unrelated Bible routes are preserved.


## Local batch 030

Adds 71 source-linked answers and 49 question groups after targeted caption-passage review across nine recordings. Existing recording reviews remain partial; remaining Q&A passages require reconciliation. Source hashes and private evidence are preserved. Audio verification is pending. Prior registry records and unrelated Bible routes are preserved.


## Local batch 031

Adds 34 source-linked answers and 28 question groups after targeted saved-caption passage review across six recordings. Remaining Q&A passages are open for reconciliation; no full-section or audio verification is claimed. Original source hashes and evidence remain private; prior records and unrelated Bible routes are preserved.


## Local batch 032

Adds 119 source-linked Dennis Murray answers and 86 question groups after targeted saved-caption passage review across ten recordings. A likely repeated Q&A export was excluded pending verification. Remaining questions stay open; no full-section or audio verification is claimed. Original source hashes and private evidence are preserved.


## Local batch 033

Adds 22 source-linked Dennis Murray answers and 16 question groups after targeted saved-caption passage review across two recordings. Remaining questions stay open; audio verification is pending. Original source hashes and evidence remain private.


## Local batch 034

Reconciles a repeated saved recording under its existing recording group and adds two source-linked Dennis answers after targeted review of held passages. One citation remains uncertain and is held for audio/context checking. No independent audio verification is claimed.


## Local batch 035

Adds three Dennis Murray linked answers and two question groups after reviewing held caption passages. Reference and classification ambiguities remain held for further checking; audio verification remains pending.


## Local batch 036

Adds seven Arnold Murray source-linked answers and three question groups from targeted saved-caption review of PC results 005. Duplicate proposals were consolidated and truncated spans extended. Remaining questions and independent audio verification are pending.


## Local batch 037

Adds 39 Arnold Murray source-linked answers and 23 question groups from targeted saved-caption review of five recordings in PC results 005. Equivalent prompts join existing groups and repeated machine proposals are consolidated. Five sources remain partial; independent audio verification remains pending. Source hashes, duplicate screening, prior registry preservation, four Python tests and both navigation suites passed.
