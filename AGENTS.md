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
- `data/state.json` — `{last_index, last_date, last_hash}`. Advanced by the
  workflow after each successful post.
- `scripts/post.py` — the poster. `scripts/templates.py` — `WORD_TEMPLATE`,
  `QUIZ_TEMPLATE` (4 rotating quiz templates). `scripts/generate_lessons.py` —
  bank generator/regenerator.
- `.github/workflows/post.yml` — workflow "Post to Telegram".
  `.github/workflows/keepalive.yml` — monthly keepalive.
- `assets/` — channel/bot logo (EVD, navy + gold). `docs/` — channel copy,
  setup guide, analytics baseline. `CHANNEL_SETUP.md`, `BOT_COMMANDS.md`,
  `RELEASE_TEST_PLAN.md`, `KPI_BASELINE.md` — ops docs.
- `logs/` — `error-log.md` (public; token redacted before write),
  `keepalive.md`.

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
  env overrides.
- Dedupe: SHA-256 of the rendered message is stored as `last_hash` in
  `data/state.json`. If the hash matches, nothing is sent. After a successful
  send the workflow commits the updated `data/state.json` (commit message
  `chore: update state YYYY-MM-DD`). That daily commit is also what keeps the
  repo active so GitHub does not disable the schedule after 60 days of
  inactivity; `keepalive.yml` (1st of month, 06:00 UTC) is the second belt.
- Retry: exponential backoff 1s/2s/4s/8s/16s on network/5xx; on Telegram 429,
  respect `retry_after` and retry once. Optional enrichment via Free
  Dictionary API (api.dictionaryapi.dev, no key); any failure falls back to
  the bank lesson. Never post broken content.
- Secrets (NAMES only — never values, never in code/chat/repo):
  `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, set in repo Settings → Secrets
  and variables → Actions. The token is embedded in the Telegram API URL, so
  `post.py` redacts `bot<digits>:<35 chars>` from any error text before
  logging (`logs/error-log.md` is committed to this public repo).
- GitHub cron is best-effort: expect 15–30 min delays sometimes.

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
- CORRECTION (2026-11-20): channel photo/description/title CAN be set via
  Bot API by the admin bot with can_change_info
  (`setChatPhoto`/`setChatDescription`/`setChatTitle`). The earlier
  "creator-only in the app" claim was wrong.
- Income honesty (never promise more): at ~10k members $65–245/month;
  $200–1,000/month needs ~20k–50k members. Stars PDF (350 Stars) earliest
  end of week 1; Telegram Ads only after 1,000 members.

## 7. Roadmap / open items

- DONE 2026-11-20: channel username confirmed; bio + pinned welcome post
  applied; bot photo/name/About/description/commands applied; test posts
  cleaned.
- OPEN: GitHub Secrets status — set by the owner, never re-verified by the
  team. Verify with a manual workflow_dispatch run (Actions → Post to
  Telegram → Run workflow), then a scheduled run.
- OPEN: monitor the first 7 days of scheduled runs; re-run manually the same
  day if one fails.
- OPEN: quiz is a text message, not a Telegram Poll (no poll votes). Poll
  quiz is a future improvement, not a launch blocker.
- OPEN: "Day N/365" label is not in post templates yet; Phrasal Verb Friday
  / Idiom Saturday are manual posts until the poster is updated.
- LATER: Stars PDF product (350 Stars) after 7 days of real content; /word
  + /quiz command handler (serverless tgcloud is the optional interactive
  add-on only — read-only, /start + /latest + search + categories, separate
  private repo, CLI token never in repo/chat).

## 8. Rules (hard)

- NEVER put a token, secret, API key, password, or private key in this repo,
  in any file, in chat, or in code. GitHub Secrets only:
  `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
- NEVER commit a file containing a secret value. Before every commit, grep
  for `bot[0-9]+:` and for secret-looking strings.
- NEVER promise income to subscribers or in channel copy. Use the honest
  ranges in §6.
- NEVER copy content from other channels, textbooks, or dictionaries. All
  examples are original to this repo.
- NEVER buy members, mass-invite strangers, or cold-DM to promote the
  channel.
- Any commit changing architecture, posting logic, automation, or external
  connections MUST update this file in the same commit.
