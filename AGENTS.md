# AGENTS.md — English Vocabulary Daily

Read this file first. It is the whole project: what it is, how it runs, what is
decided. Do not reverse-engineer; follow it. Update it in the same commit as
any change to architecture, posting logic, automation, or external connections.

## 1. What this is

English Vocabulary Daily is a Telegram channel that posts one English word
every morning and a quiz on that word every evening, fully automated, free
(GitHub Actions only, no AI at runtime, no paid services). Content comes from
a fixed lesson bank in this repo. Owner: halakouai-byte. Channel language:
English. Owner language: Persian.

## 2. Tech stack + repo layout

- Python 3.12, stdlib + `requests`. No other dependencies, no AI at runtime.
- `data/lessons.json` — the lesson bank, v2, 1,446 lessons. Source of truth.
  Fields per lesson: `word`, `meaning`, `phonetic`, `example` (a real sentence
  using the word), `synonyms`, `type`, `quiz_q`, `quiz_options` (4),
  `quiz_a` (always one of the options).
- `data/words.txt` — the word list, 1,446 words, same order as the bank.
- `data/lessons-fixed-v2.json` — provenance copy of the v2 bank (identical
  to `lessons.json`).
- `data/state.json` — `{last_index, last_date, last_hash, last_kind}`. Advanced by the
  workflow after each successful post. `last_kind` is "word" or "quiz" — the
  watchdog uses it to tell which post is missing.
- `scripts/post.py` — the poster (word = Markdown message; quiz = Telegram
  Poll via `build_poll` + `send_poll`). `scripts/templates.py` —
  `WORD_TEMPLATE` (word post, with `Day {day}/365` label).
  `scripts/generate_lessons.py` — bank generator/regenerator.
- `.github/workflows/post.yml` — workflow "Post to Telegram".
  `.github/workflows/watchdog.yml` — hourly catch-up: dispatches post.yml
  with the missing kind when a slot is overdue (see §4).
  `.github/workflows/keepalive.yml` — monthly keepalive.
  `.github/workflows/secret-scan.yml` — workflow "Secret scan" (gitleaks
  v8.28.0, full history, fails on any finding).
- `assets/` — channel/bot logo (EVD, navy + gold). `docs/` — channel copy,
  setup guide, analytics baseline. `CHANNEL_SETUP.md`, `BOT_COMMANDS.md`,
  `RELEASE_TEST_PLAN.md`, `KPI_BASELINE.md` — ops docs.
- `logs/` — `error-log.md` (public; token redacted before write),
  `keepalive.md`, `watchdog.md` (watchdog activity — one line per overdue
  slot or dispatch, nothing on no-op hours).

## 3. Validate + dry-run (run from repo root)

```bash
pip install requests
python3 -m json.tool data/lessons.json > /dev/null   # bank must parse
python3 - <<'EOF'                                    # bank QA: 1,446 lessons, no empties, valid quizzes
import json
d = json.load(open('data/lessons.json'))
assert len(d) == 1446, len(d)
assert len({x['word'] for x in d}) == 1446
for x in d:
    assert x['word'] and x['meaning'] and x['example'] and x['type']
    assert len(x['quiz_options']) == 4 and x['quiz_a'] in x['quiz_options']
    assert len(set(x['quiz_options'])) == 4
print('bank OK: 1446 lessons')
EOF
python3 scripts/post.py                              # dry-run: prints the message, sends nothing, does not touch state
POST_KIND=word python3 scripts/post.py               # force the morning word post
POST_KIND=quiz python3 scripts/post.py               # force the evening quiz post
```

Do NOT run `scripts/generate_lessons.py` to validate: it regenerates
`data/lessons.json` from `data/words.txt` (re-serialized + rebuilt quiz
distractors) and its output is NOT identical to the QA-passed v2 bank in the
repo. The v2 bank in the repo is the source of truth. Only run the generator
when intentionally rebuilding the bank, then re-run the full QA above before
committing anything.

Dry-run rule: if `TELEGRAM_BOT_TOKEN` or `TELEGRAM_CHAT_ID` is unset,
`post.py` prints instead of sending and exits 0. Never test with real
credentials on a local machine; use the dry-run or a manual
`workflow_dispatch`.

## 4. Deployment + automation

- Workflow "Post to Telegram" (`.github/workflows/post.yml`): schedule
  `15 7,17 * * *` (07:15 + 17:15 UTC daily), plus `workflow_dispatch`.
  `permissions: contents: write`. Concurrency group `post`, no cancellation.
- Post selection is deterministic: word =
  `lessons[day_of_year % len(lessons)]`. UTC hour < 12 posts the word;
  >= 12 posts the quiz on the morning word + yesterday's answer. `POST_KIND`
  env overrides. Word posts carry `🗓️ *Day {day}/365*` after the title.
  The quiz is a Telegram Poll (`sendPoll`, type=quiz): question
  `Day {day}/365: {quiz_q}`, 4 options, `correct_option_id` = index of
  `quiz_a`, `explanation` = yesterday's answer (cut to 200 chars).
- Dedupe: SHA-256 of the rendered message is stored as `last_hash` in
  `data/state.json`. If the hash matches, nothing is sent. After a successful
  send the workflow commits the updated `data/state.json` (commit message
  `chore: update state YYYY-MM-DD`). That daily commit is also what keeps the
  repo active so GitHub does not disable the schedule after 60 days of
  inactivity; `keepalive.yml` (1st of month, 06:00 UTC) is the second belt.
  State also records `last_kind` ("word"/"quiz") so the watchdog knows which
  post is missing. Word posts hash the rendered text; quiz polls hash the
  canonical poll payload (question + options + correct answer).
- Retry: exponential backoff 1s/2s/4s/8s/16s on network/5xx; on Telegram 429,
  respect `retry_after` and retry once. Optional enrichment via Free
  Dictionary API (api.dictionaryapi.dev, no key); any failure falls back to
  the bank lesson. Never post broken content.
- Secrets (NAMES only — never values, never in code/chat/repo):
  `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, set in repo Settings → Secrets
  and variables → Actions. The token is embedded in the Telegram API URL, so
  `post.py` redacts `bot<digits>:<35 chars>` from any error text before
  logging (`logs/error-log.md` is committed to this public repo).
- GitHub cron is best-effort: delays of hours happen and a scheduled event
  can be dropped entirely — 2026-11-20 the 17:15 run started ~5h48m late;
  2026-11-21 the 07:15 run was never created. `watchdog.yml` runs hourly
  and catches a missed slot: word if nothing posted today by 10:00 UTC,
  quiz if only the word posted by 19:00 UTC. It dispatches post.yml with
  `POST_KIND`; post.py dedupes by hash, so a late scheduled run only skips.
  The watchdog never dispatches while a post.yml run is queued/running.
  Every overdue slot or dispatch is recorded as one line in
  `logs/watchdog.md` (committed back to the repo, same pattern as
  keepalive); no-op hours log nothing. `watchdog.yml` needs
  `permissions: contents: write` for that commit.
- Leak protection (Layer 1): workflow "Secret scan"
  (`.github/workflows/secret-scan.yml`) runs on push, on pull_request, and
  weekly (Sunday 03:00 UTC). It checks out the full history
  (`fetch-depth: 0`), downloads pinned gitleaks v8.28.0, verifies its SHA256
  before extracting, then runs `/tmp/gitleaks git --verbose --exit-code 1`
  — the workflow FAILS on any finding. No token of any kind is used by this
  workflow. Layer 2 (GitHub native Secret scanning + Push protection +
  CodeQL) and Layer 3 (manager sweep) are enabled/verified outside this
  repo's files.

## 5. External services (names only)

- Telegram bot: @learnvocabularydailybot. Telegram channel:
  @learnvocabularydaily. GitHub repo: halakouai-byte/english-vocab-daily
  (public).
- No other services. No secret values in this file, anywhere in the repo,
  or in chat.

## 6. Key decisions + history

- 2026-11-18: repo created (public). Channel niche chosen after a
  15-criteria team review: English Vocabulary Daily, 14/15 (criterion 8
  conditional — bank in repo + free APIs as enrichment, not 5 daily feeds).
- 2026-11-18: v1 content audit verdict FIX-FIRST — 0 real example sentences
  in 1,430 lessons (all 8 meta-templates), ~11% error rate in a 120-lesson
  sample. Do not launch v1 as-is.
- 2026-11-18/19: v2 fix — 1,071 examples rewritten as real, original
  sentences; bank grew to 1,446 lessons (17 base words added, `spoke`
  removed as past tense); quiz distractors rebuilt same-part-of-speech;
  4 rotating quiz templates; generator fixed so existing examples are never
  overwritten (new word → empty example + warning + exit 2). Automated QA on
  all 1,446 lessons: 0 meta templates, 0 empty fields, 0 broken quizzes,
  0 circular synonyms, 0 shared meanings.
- 2026-11-19: the old upload zip (20:45, 2026-11-18) is pre-v2 — never use
  it. Current package is `english-vocab-daily-upload-v2.zip` (12 files).
- 2026-11-20 16:29 Tehran: first live test — manual "Post to Telegram" run
  #1 posted lesson index 324 "fill"; state commit `42bd84a`.
- 2026-11-20 17:15 UTC: first scheduled run did not start by 17:48 UTC
  (missed/delayed; fresh-workflow GitHub cron behaviour). Manual re-run is
  the fallback.
- 2026-11-20 23:37 Tehran: channel confirmed @learnvocabularydaily; bot
  verified admin (post/edit/delete/manage/change-info true; promote false).
- 2026-11-20 ~23:52 Tehran: bot + channel setup applied via Bot API and
  read-back verified: bot photo (`setMyProfilePhoto` — the `photo` field must
  be JSON `{"type":"static","photo":"attach://logo"}` with the file under a
  separate `logo` field; a bare file under `photo` fails with "photo isn't
  specified"), name/About/description/commands (start + help only — no
  command handler exists yet, so no /word or /quiz on the menu), channel
  photo/title/bio (164 chars), welcome post sent by the bot and pinned
  (message_id 5). Test posts 3–4 deleted 23:53; pinned post kept.
- 2026-11-21: local working tree had drifted from the live bank (a second
  variant from the round-2 content edit, different quiz distractors);
  local `data/lessons.json` was restored from the live repo so local ==
  remote == `lessons-fixed-v2.json`. The v2 bank is the only source of truth.
- 2026-11-21: leak protection Layer 1 added — `.github/workflows/
  secret-scan.yml` (gitleaks v8.28.0, SHA256-verified, full history, fails
  on any finding; triggers push + pull_request + weekly). One-time
  full-history audit 2026-11-21 found 0 findings in all repos; the first
  CI run of this workflow must confirm 0 findings again. Pattern copied
  from liveforge's `build.yml` (same pinned version and scan command).
- CORRECTION (2026-11-20): channel photo/description/title CAN be set via
  Bot API by the admin bot with can_change_info
  (`setChatPhoto`/`setChatDescription`/`setChatTitle`). The earlier
  "creator-only in the app" claim was wrong.
- 2026-11-21 07:15 UTC: scheduled morning run NEVER created by GitHub
  (checked 13:14 UTC — no run #3 in the Actions list). Manager dispatched
  post.yml manually; run #3 posted the quiz for lesson 325 "final" at
  13:16 UTC (state commit `a6b86fc`). The word for 325 never posted —
  hour-based kind selection sent a quiz instead of the missing word.
  Cause: GitHub's best-effort scheduler dropped the event; no repo-side
  defect (same file ran fine at 17:15 the same day). Fix: `watchdog.yml`
  (hourly catch-up) + `last_kind` in state.
- 2026-11-21 17:15 UTC: scheduled run #4 ran (18s). No new post and no
  state change — consistent with the expected dedupe-skip (quiz 325 was
  already posted at 13:16 UTC).
- 2026-11-22: bot menu emptied (`setMyCommands` with an empty list —
  /start + /help removed until a command handler exists; /help advertised
  a "free PDF" that doesn't exist). Quiz is now a Telegram Poll
  (`sendPoll`, type=quiz) with the `Day N/365` label in the question;
  word posts carry the label in the template. The watchdog now logs every
  overdue slot or dispatch to `logs/watchdog.md`.
- Income honesty (never promise more): at ~10k members $65–245/month;
  $200–1,000/month needs ~20k–50k members. Stars PDF (350 Stars) earliest
  end of week 1; Telegram Ads only after 1,000 members.

## 7. Roadmap / open items

- DONE 2026-11-20: channel username confirmed; bio + pinned welcome post
  applied; bot photo/name/About/description/commands applied; test posts
  cleaned.
- DONE 2026-11-21: GitHub Secrets proven — three live posts (manual run #1,
  scheduled run #2, manual run #3) all used `TELEGRAM_BOT_TOKEN` +
  `TELEGRAM_CHAT_ID` successfully.
- OPEN: monitor the first 7 days of scheduled runs; re-run manually the same
  day if one fails.
- OPEN: watchdog.yml added 2026-11-21 — watch the first week: it must
  dispatch within ~1h of a missed slot and never double-post (dedupe is
  the backstop).
- DONE 2026-11-22: quiz is a Telegram Poll (`sendPoll`, type=quiz,
  correct_option_id, explanation = yesterday's answer).
- DONE 2026-11-22: "Day N/365" label — word template + poll question.
- OPEN: Phrasal Verb Friday / Idiom Saturday are manual posts until the
  poster is updated.
- LATER: Stars PDF product (350 Stars) after 7 days of real content; /word
  + /quiz command handler (serverless tgcloud is the optional interactive
  add-on only — read-only, /start + /latest + search + categories, separate
  private repo, CLI token never in repo/chat).

## 8. Rules (hard)

- NEVER put a token, secret, API key, password, or private key in this repo,
  in any file, in chat, or in code. GitHub Secrets only:
  `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
- NEVER commit a file containing a secret value. Before every commit, grep
  for `bot[0-9]+:` and for secret-looking strings. The CI secret scan
  (`secret-scan.yml`) enforces this on every push and PR — a finding fails
  the run.
- NEVER promise income to subscribers or in channel copy. Use the honest
  ranges in §6.
- NEVER copy content from other channels, textbooks, or dictionaries. All
  examples are original to this repo.
- NEVER buy members, mass-invite strangers, or cold-DM to promote the
  channel.
- Any commit changing architecture, posting logic, automation, or external
  connections MUST update this file in the same commit.


## 9. GitHub read/write rule (standing, owner order 2026-11-21)

- READS only via the GitHub connector: HEAD, files, commits, repo status,
  logs. Never read the repo any other way.
- WRITES never via the connector: never use a connector write tool and
  never send a write-approval card to the owner. All pushes, commits,
  branches, and anything that changes the repo or the site go through the
  browser, done by the manager (Muse in the management chat).
- The team prepares the write (files + exact commit message) and hands it
  to the manager; the manager commits it via the browser.
