# English Vocabulary Daily

An English-only Telegram channel that posts one vocabulary word every morning
and a quiz every evening — **fully automated with GitHub Free, no AI at runtime**.

- **Channel:** English Vocabulary Daily
- **Likely username:** `@englishworddaily` — ⚠️ **TO CONFIRM.** The user built the
  channel but has not confirmed the exact username. Do not assume this is final;
  update this README and the channel link once confirmed in the Telegram app.
- **Language:** English only, global audience.
- **Cost:** $0 — public GitHub repo, GitHub Actions free tier, Telegram Bot API free.

## How it works

1. GitHub Actions runs on a schedule: `15 7,17 * * *` — **07:15 and 17:15 UTC**.
2. `scripts/post.py` picks the word deterministically:
   `index = day_of_year % len(lessons)` — no randomness, no LLM, no API call
   required to choose the word.
3. Morning run (07:15 UTC) posts **Word of the Day**: word + IPA phonetic +
   meaning + original example sentence + synonyms.
4. Evening run (17:15 UTC) posts a **4-option quiz** on the morning word +
   yesterday's answer.
5. After a successful post, the workflow commits the updated
   `data/state.json` back to the repo. That commit is what keeps the repo
   active, so GitHub does **not** disable the scheduled workflow after
   60 days of inactivity. A monthly `keepalive.yml` run is a second safety net.

Content lives in `data/lessons.json` (1,446 lessons — almost 4 years of daily
words). Each lesson is `{word, meaning, phonetic, example, synonyms,
quiz_q, quiz_options (4), quiz_a, type}`. All example sentences are original,
written for this repo. No copied text from BBC, Duolingo, or textbooks.

## No AI at runtime

- The poster uses **only Python stdlib + `requests`**.
- There is **no LLM call, no AI API, no paid API** in the daily run.
- AI was used only to help write the code and the lesson bank once, during
  setup — never to generate a daily post.
- Optional enrichment only: the Free Dictionary API (`dictionaryapi.dev`,
  no key) may add a phonetic if the bank one is missing. If it fails, the
  post still goes out from the bank. Enrichment is never required.

## Sources & attribution

- **Lesson bank (`data/lessons.json`, `data/words.txt`):** all 1,446 words,
  meanings, example sentences and quizzes are original content written for
  this repo. No text was copied from BBC, Duolingo, textbooks or any other
  published course. Example sentences are built from fixed original
  templates plus each word's own meaning.
- **Optional enrichment only:** the Free Dictionary API
  (`https://api.dictionaryapi.dev`, no API key required) may supply a
  phonetic pronunciation if the bank entry has none. It is never required
  for a post, and it never replaces the bank meaning. If it fails, the bank
  lesson is posted as-is.
- **No other sources:** the daily run fetches nothing else, and there is no
  scraped or third-party content in the channel posts.

## Licence

- **Code and workflows** (`scripts/`, `.github/workflows/`, `README.md`,
  `BUILD_REPORT.md`): MIT — see `LICENSE`.
- **Lesson bank** (`data/lessons.json` and `data/words.txt`): licensed
  separately under **CC BY 4.0** (Creative Commons Attribution 4.0
  International). You may share and adapt the word list and lessons for any
  purpose, including commercially, provided you give appropriate credit to
  "English Vocabulary Daily", link to the licence
  (https://creativecommons.org/licenses/by/4.0/), and indicate any changes
  you made. The MIT licence in `LICENSE` does **not** cover the lesson bank.

## GitHub Free limits (verified 18 Nov 2026)

- **Public repo: GitHub Actions is free and unlimited.** (Private repos get
  2,000 minutes/month — this repo must stay public.)
- Each run takes ~1.5 minutes → 2 posts/day ≈ **90 minutes/month**
  (0% of a private quota, $0 public). 10 posts/day would be ~450 min/month,
  still $0 on a public repo.
- Cron minimum interval is 5 minutes; scheduling is best-effort — expect a
  15–30 minute delay sometimes, and occasionally a missed run. Never promise
  an exact posting minute.
- One job timeout is 6 hours; we set `timeout-minutes: 5`.
- Repo secrets: max 100 per repo — we use only 2.
- Storage: `lessons.json` is under 2 MB, far below the 500 MB artifact /
  10 GB cache limits. GitHub Pages is not needed for this channel.

## Setup (live since 2026-11-20)

The repo is live at https://github.com/halakouai-byte/english-vocab-daily and posts twice a day. This is how it was set up:

1. **Create the bot:** in Telegram, open `@BotFather`, send `/newbot`,
   copy the token.
2. **Add the bot to your channel** as an admin with permission to post.
3. **Get the channel chat ID:** the easiest way is to forward a channel post
   to `@userinfobot` or `@getmyid_bot`, or use the Bot API `getUpdates`
   after the bot is admin — it is a negative number for channels
   (e.g. `-1001234567890`). Do **not** share the token or chat ID publicly.
4. **Add GitHub secrets** (repo → Settings → Secrets and variables → Actions):
   - `TELEGRAM_BOT_TOKEN` — the BotFather token
   - `TELEGRAM_CHAT_ID` — the channel chat ID
5. **Test manually:** Actions → "Post to Telegram" → Run workflow.
   Or test locally first (see below).
6. **Confirm the username** in the Telegram app and update this README.

> Never commit `TELEGRAM_BOT_TOKEN` or `TELEGRAM_CHAT_ID` to the repo.
> If a token ever leaks, revoke it in BotFather with `/revoke` and issue a new one.

## Test locally (dry-run, no token needed)

```bash
pip install requests
# Morning word (dry-run prints instead of sending):
python3 scripts/post.py
# Evening quiz:
POST_KIND=quiz python3 scripts/post.py
# Force morning word regardless of time:
POST_KIND=word python3 scripts/post.py
```

If `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` are missing, the script prints
the message and exits 0 without sending and without updating state.
To send for real locally, export both variables first — only for a test,
prefer the GitHub workflow run instead.

## Files

```
.github/workflows/post.yml       # cron 07:15 + 17:15 UTC, posts + commits state
.github/workflows/keepalive.yml  # monthly keepalive commit
scripts/post.py                   # poster: stdlib + requests only, no AI
scripts/templates.py              # fixed message templates
scripts/generate_lessons.py       # rebuilds lessons.json from data/words.txt
data/lessons.json                 # 1,446 lessons
data/words.txt                    # source word list (word|phonetic|meaning|synonyms|type)
data/state.json                   # {last_index, last_date, last_hash}
README.md / BUILD_REPORT.md / LICENSE (MIT) / data/LICENSE (CC BY 4.0) / .gitignore
```

## Safety / dedupe / retries

- **Dedupe:** SHA-256 of the rendered message is stored in `state.json`.
  A second run with the same content is skipped — no duplicate posts.
- **Retries:** exponential backoff (1s, 2s, 4s, 8s, 16s) on network/5xx errors.
- **Rate limit:** on Telegram 429, the script respects `retry_after`
  (capped at 120s) and retries once.
- **Broken content:** if a lesson is missing a field or a quiz answer is not
  one of the options, the run fails loudly and posts nothing.
- **Fallback:** if the Dictionary API fails, the bank lesson is used as-is.
- **Error log:** `logs/error-log.md` is written by the runner for debugging
  only and is **never committed to the repo** (the workflow commits
  `data/state.json` only). Error messages are redacted in `scripts/post.py`
  before logging, so the bot token can never appear in a log line.

## Still needed

- Confirm the exact channel username (`@englishworddaily` is a placeholder —
  the channel exists, but the exact username is unconfirmed; update this
  README once confirmed in the Telegram app).
- The bot token and channel chat ID are already stored as GitHub secrets
  (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`) — never in chat or in the repo.
