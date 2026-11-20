# Build Report — English Vocabulary Daily automation repo

> **Erratum (2026-11-21):** this is the original 2026-11-18 build log, kept as history. The lesson bank is **1,446 lessons (686,392 bytes)**, not 1,430 (768 KB) as written below, and the repo is now live on GitHub — first post published 2026-11-20. The "not connected / do not push" notes below are outdated; the connection works.

Built locally on 2026-11-18. **Ready to push to GitHub once GitHub is connected.
Nothing has been pushed — GitHub is not connected yet, so pushing is blocked.**

## Files created

```
telegram-english-vocab/
├── README.md                          # English, setup, GitHub Free limits
├── BUILD_REPORT.md                    # this file
├── LICENSE                            # MIT
├── .gitignore                         # __pycache__, .venv, .env
├── .github/workflows/post.yml         # cron '15 7,17 * * *', Python 3.12,
│                                      #   concurrency: post, timeout-minutes: 5,
│                                      #   commits data/state.json back
├── .github/workflows/keepalive.yml    # monthly keepalive, 1st of month
├── scripts/post.py                    # poster — stdlib + requests only, no AI
├── scripts/templates.py               # fixed WORD_TEMPLATE / QUIZ_TEMPLATE
├── scripts/generate_lessons.py        # rebuilds lessons.json from words.txt
├── data/lessons.json                  # 1,430 lessons (768 KB)
├── data/words.txt                     # source word list (1,430 lines)
├── data/state.json                    # {"last_index": -1, "last_date": "", "last_hash": ""}
└── logs/                              # error-log.md / keepalive.md created at runtime
```

## Lesson bank

- **Count: 1,430 lessons** (requirement was ≥365 — this is ~3.9 years of daily words).
- **Unique words (case-insensitive): 1,430 — zero duplicates.**
- **Types:** noun 638, verb 393, adjective 303, adverb 86, idiom 5, phrasal verb 5.
- **Every lesson has:** `word, meaning, phonetic, example, synonyms (array),
  quiz_q, quiz_options (4), quiz_a` (+ `type`). Verified: 0 bad lessons,
  and `quiz_a` is always one of `quiz_options`.
- Examples are original sentences written for this repo (fixed templates +
  per-word meaning). No copied text from BBC, Duolingo, or textbooks.

## Verification (all passed, 2026-11-18)

- `python3 -m json.tool data/lessons.json` — **OK**
- Lesson count ≥365 — **1,430 ✓**
- No duplicate words — **0 dupes ✓**
- All required fields + quiz_a ∈ quiz_options — **0 bad ✓**
- `python3 -m py_compile scripts/post.py scripts/templates.py scripts/generate_lessons.py` — **OK**
- Workflow YAML parses (`yaml.safe_load`) for `post.yml` + `keepalive.yml` — **OK**
- Dry-run `POST_KIND=word python3 scripts/post.py` — **exit 0**, prints the
  Word of the Day, sends nothing, state unchanged.
- Dry-run `POST_KIND=quiz python3 scripts/post.py` — **exit 0**, prints the
  quiz + yesterday's answer, sends nothing, state unchanged.
- One bug found and fixed during testing: the enrichment call passed the
  whole lesson dict instead of the word string, and used the wrong
  `urllib` quote helper. Fixed, re-tested — dry-run is now clean.

## How to test locally (dry-run)

```bash
pip install requests
POST_KIND=word python3 scripts/post.py   # morning word, printed not sent
POST_KIND=quiz python3 scripts/post.py   # evening quiz, printed not sent
```

When `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` are missing, the script prints
the message and exits 0 without sending and without updating `data/state.json`.
That is the dry-run mode.

## What still needs the user (blocked)

1. **GitHub connection** — GitHub is not connected yet. Do not push until it is.
   Then: create a **public** repo and push this folder.
2. **BotFather token** — create the bot in Telegram, copy the token.
3. **Channel chat ID** — add the bot as channel admin, get the chat ID
   (negative number for channels).
4. **Add GitHub secrets** `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`
   (never commit them, never share them in chat).
5. **Confirm the exact channel username** — `@englishworddaily` is used in
   the README as a **TO-CONFIRM placeholder**. The user built the channel
   but has not confirmed the exact username. Update README once confirmed
   in the Telegram app.
6. **First live test:** Actions → "Post to Telegram" → Run workflow, then
   check the channel for the post.
