# Lesson Bank Fix Report — v2

**Date:** 2026-11-18 (local-only work; GitHub blocked with 403)
**Source (READ ONLY, untouched):** `data/lessons.json`
**Fixed output:** `data/lessons-fixed-v2.json`
**Fix script:** `/tmp/fix_lessons_v2.py` (deterministic; re-runnable)

## IMPORTANT: the brief described an older file

The task brief said the source had 1,430 lessons, 8 repeated meta templates
(`"Learning the word 'X'... It means: <meaning>"`), ~30 mistyped adverbs,
13 sample errors, and a duplicate word `spoke`.

**The live source file is not that file.** It is already the output of an
earlier fix run (`/tmp/fix_lessons.py`, present in /tmp): **1,446 lessons**,
0 duplicates, 0 empty fields, real example sentences, correct types.
Verified against the live file before fixing:

| Audit claim (old file) | Live source (before v2) | Status |
|---|---|---|
| 1,430 lessons | **1,446 lessons** | Brief was stale; v2 keeps 1,446 |
| 8 meta templates, "It means:" | 0 occurrences of "It means:" | Already fixed |
| ~30 mistyped adverbs | 0 — although/despite/except/itself/myself/neither/since/that/which/who/whose/with/without are all correctly typed already | Already fixed |
| 13 sample errors (north, surface, neck, should, balance/paint/close/request...) | All already correct in live source | Already fixed |
| Duplicate word `spoke` | `spoke` absent; `speak` present once | Already fixed |
| 0 dual meanings (", or ") | 0 in live source | Already fixed |
| First 30 lessons hard (abandon…allow) | First 30 already easy A1: day, water, house, friend, happy, book, school, cat, dog, sun, mother, father, family, child, man, woman, boy, girl, red, blue, big, small, good, bad, new, old, hot, cold, eat, drink | Already fixed |
| Ambiguous quiz for `log` ("wood" also correct) | `log` quiz options do not contain `wood`'s meaning | Already fixed |

Source md5 for the final rebuild was verified unchanged before and after
(`edc384437d723d83e12da7fb7db5a5b4` both times). Earlier in this task the
source changed twice under concurrent editing by another agent
(`f5b0d5…` → `28ef92ea…` → `6a7916e9…` → `edc38443…`); see "Rebuild note"
above. `lessons.json` itself was never written by this task.

## What v2 actually fixed (real remaining problems)

**Rebuild note (important):** this file was rebuilt a second time because
`lessons.json` changed under this task — md5 trail `f5b0d5…` → `28ef92ea…` →
`6a7916e9…` → `edc38443…` — another agent was editing the same source
concurrently. The first v2 build (from `28ef92ea…`) rewrote 72 weak examples
with the sentences listed in `/tmp/fix_lessons_v2.py`. The rebuild (from the
current `edc38443…`, source md5 stable before/after) found those 72 examples
already fixed by the other agent with their own real sentences (e.g. abandon:
"He abandoned his old car in the forest and walked home."), so it preserved
them instead of overwriting — the script only replaces an example if it is
still a weak template. Final v2 below is built from `edc38443…`.

| Problem | Before (current source) | After (v2) |
|---|---|---|
| Weak generic verb examples ("He Xs it with great care." ×30, "She Xs it every day." ×27, plus 4 more templates) | 0 — already fixed by the other agent before the rebuild | **0** — none left; v2 rewrote 0 (first build had rewritten 72) |
| Distinct example templates | 1,369 in the earlier snapshot; 1,436 in the current source | **1,436** (max repeat 3) |
| Quiz distractor part-of-speech mismatch | 2,950 / 4,338 (68%) — distractors were random meanings, so most quizzes were solvable by deleting the wrong part of speech | **3 / 4,338 (0.07%)** — distractors rebuilt from same-type meanings |
| Quiz question templates | 1,436 × `What does "X" mean?` (+ 5 idiom / 5 phrasal) | 4 templates rotated evenly: 359 each of `What does…`, `Choose the correct meaning of…`, `Which of these means…`, `"X" means…?` (idiom/phrasal wording kept) |
| `please` sense/type mismatch | verb, "to make someone happy", example "I want to please my teacher." — internally consistent in the verb sense, but the A1 polite-word sense is the one learners need first | **adverb**, "used to be polite when you ask for something", example "Please sit down.", synonyms ['kindly'] |
| `rest` sense/example mismatch | noun "what is left" with example "Please rest after lunch." (verb sense) | noun "a time when you relax and do nothing", synonyms ['relaxation', 'sleep'] |
| `stick` wrong synonym | already ['fasten', 'glue'] in the current source | unchanged (already correct) |
| `mention` / `refer` near-identical meanings | `refer` = "to mention something or point to it" vs `mention` = "to talk about something briefly" | `refer` = "to speak or write about something"; both meanings now excluded from each other's quiz options |
| `sick` circular synonym | synonyms ['ill'] (ill lists sick back) | synonyms ['unwell', 'poorly'] |
| Mutual (circular) synonym pairs | 225 undirected pairs (450 directed) | **21 undirected pairs (42 directed)** — 203 directions removed where the word kept another synonym |
| Quizzes rebuilt (deterministic, seed = word) | — | **1,446** |

**Counts (final rebuild):** lessons changed vs current source 1,446 (every
lesson — quiz rebuild touched all of them); examples rewritten by v2: **0**
(the other agent had already rewritten the 72; first v2 build had rewritten
72 from the earlier snapshot); targeted sense/type fixes **8** field changes
across 4 words (`please` ×4, `rest` ×2, `refer` ×1, `sick` ×1);
circular-synonym directions removed 203.

## Verification (re-run independently on the output file, not just the script)

- JSON parses: OK
- Count: **1,446** lessons in, **1,446** out (the brief's "1,430" is the stale pre-fix count; no lesson was deleted to force it)
- 0 duplicate words (case-insensitive); `spoke` absent
- Every lesson has all required fields (word, meaning, phonetic, example, synonyms, quiz_q, quiz_options, quiz_a, type); 0 empty fields
- Every `quiz_a` is one of its 4 options; every option list has 4 distinct options
- 0 example fields match the old meta templates; 0 contain "It means:"
- 0 weak generic templates remain
- Word order unchanged (same order as source, first 30 still the A1 list above)

## Remaining issues (honest)

1. **`yes` (the only interjection, 1 of 1,446):** its 3 quiz distractors must come from other parts of speech — there is no other interjection in the bank. This is the entire remaining 3/4,338 distractor mismatch. Fix would need a second interjection lesson (e.g. "oh" / "wow") added to the bank.
2. **`ill` / `sick` near-identical meanings** ("not in good health" / "not well") remain as two separate lessons — a genuine near-duplicate pair. Mitigated, not solved: neither meaning ever appears as a distractor in the other's quiz, so no quiz has two correct answers.
3. **21 mutual synonym pairs remain**, all cases where removing a direction would leave a word with zero synonyms. They are ordinary synonymy (e.g. `book` ↔ `novel`), not errors, but the count is reported here rather than hidden.
4. **Phonetics** were not re-checked in v2 (the earlier run converted rhotic forms to RP); a spot check shows mixed RP forms remain possible. A full IPA audit is still open.
5. The 18 examples that use an inflected form instead of the base word (drank, carried, gave…) were **kept deliberately** — they are correct natural usage, not errors.
