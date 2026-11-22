# Channel Setup — English Vocabulary Daily

**Status:** 18 November 2026 · Setup guide, not a live check. Updated 20 November 2026 — channel username confirmed (see below).
**Channel username:** `@learnvocabularydaily` — **CONFIRMED** 20 November 2026 by user link. Channel link: https://t.me/learnvocabularydaily
**Channel ID:** `-1004348347589` (channel id is not a secret). **Channel title:** "learn vocabulary daily".

**What this file is:** the complete 0-to-100 paper setup for the channel and
bot. It does not post anything, does not touch Telegram, and does not contain
any bot token. Never put a bot token in this repo, in chat,
or in any file. (The channel ID `-1004348347589` is listed in this file
because a channel id is not a secret; it is not a token.)

**Verified facts this file is built on**

- Channel already built by the user; bot made admin in the channel (user
  confirmed 18 Nov 2026, 23:49 Tehran). This is the user's statement — it has
  **not** been independently verified by any agent. Verification is in
  progress; do not mark it verified on the basis of this file alone.
- Channel name: **English Vocabulary Daily**
- Channel username (confirmed 20 Nov 2026): **@learnvocabularydaily** —
  https://t.me/learnvocabularydaily — channel ID `-1004348347589`, title
  "learn vocabulary daily".
- Bio (164 chars, use verbatim):
  > One new English word every morning + an evening quiz. Word of the Day • IELTS vocabulary • Idioms & phrasal verbs. Free, just 2 min a day. Join & start Day 1 today.
- Posting: Word of the Day **07:15 UTC**, quiz **17:15 UTC**, via GitHub
  Actions (`scripts/post.py`, cron `15 7,17 * * *`). GitHub cron is
  best-effort — expect a 15–30 minute delay sometimes.
- Weekly rhythm: **Phrasal Verb Friday**, **Idiom Saturday**.
- Monetization: Stars PDF **"365 Words + Quiz" — 350 Stars (~$4.55/sale)**.
  Telegram Ads only after **1,000 members**. At ~10,000 members realistic
  income is only **$65–245/month**. **$200–1,000/month needs ~20,000–50,000
  members.** Never promise income to the user or to subscribers.
- Repo: public GitHub repo, 1,430 lessons in `data/lessons.json`.

**⚠️ Two gaps to fix before launch (not blockers for this checklist, but do
not claim they are already done)**

1. **"Day N/365" is not in the current post templates.** The growth plan
   requires Day N/365 on every post, but `scripts/templates.py` today has no
   Day line. Either add it to the templates before launch, or add "Day N"
   manually to backup posts. Do not tell subscribers the Day number is
   automatic until the template actually prints it.
2. **Friday/Saturday themes are not automated.** `post.py` picks the word
   deterministically by day of year; it does not switch to a phrasal verb on
   Friday or an idiom on Saturday. Until a template/schedule change is made,
   Phrasal Verb Friday and Idiom Saturday are **manual posts** (see §6).

---

## 1. Bot admin check

Do this in the Telegram app, on the phone/desktop where the channel was built.

- [ ] Open the channel → tap the channel name → **Edit** (pencil) →
      **Administrators** → confirm the bot is listed as an admin.
- [ ] Tap the bot in the Administrators list and check its permissions:
  - [ ] **Post Messages: ON** — the only permission the bot needs.
  - [ ] **Edit Messages: OFF** (not needed; the poster never edits).
  - [ ] **Delete Messages: OFF**
  - [ ] **Add Subscribers / Invite Users: OFF**
  - [ ] **Manage Channel / Change Channel Info: OFF**
  - [ ] **Add Admins: OFF**
  - [ ] **Post Stories: OFF**
  - [ ] **Manage Live Streams / Manage Video Chats: OFF**
  - [ ] **Anonymous / Remain Anonymous: OFF**
- [ ] If the bot is **not** in the Administrators list: channel → Edit →
      Administrators → **Add Admin** → search the bot's username → add it,
      then set permissions exactly as above.
- [ ] Confirm the bot is **not** also an admin anywhere it should not be
      (no other channels/groups).
- [ ] Do **not** give the bot the channel owner's rights, and do **not**
      share the bot token with anyone. If a token ever leaks, revoke it in
      `@BotFather` with `/revoke` and issue a new one, then update the GitHub
      Secret (see `BOT_COMMANDS.md`).

**Why Post Messages only:** least privilege. A bot that can only post cannot
invite people, change the channel name/bio, add other admins, or delete
history. If posting ever fails with "not enough rights", this checklist is
the first thing to re-check — it is the most common cause.

---

## 2. Channel name, bio, and photo

- [ ] **Name** — set exactly: `English Vocabulary Daily`
  - Channel → Edit → **Channel Name**. No emoji in the name, no extra words
    (no "Official", no "Free PDF" in the name — that belongs in the bio/pins).
- [ ] **Bio / Description** — paste verbatim (164 characters):
  > One new English word every morning + an evening quiz. Word of the Day • IELTS vocabulary • Idioms & phrasal verbs. Free, just 2 min a day. Join & start Day 1 today.
  - [ ] Count check: 164 characters (verified). The old version's "174 chars"
        claim was wrong — the old string was actually 172 characters. Use
        the new 164-char version above.
  - [ ] No link in the bio yet. Add the channel's own t.me link only after
        the username is confirmed. (Username is now confirmed:
        https://t.me/learnvocabularydaily — the link may be added.)
- [ ] **Photo** — text/icon only, no copied logos:
  - [ ] Simple, original design: the letters **"EVD"** or a single open-book /
        word-bubble icon on a solid dark background, white or gold text.
  - [ ] **Do not** use a Duolingo owl, BBC logo, Oxford/Cambridge crest, or
        any stock photo or textbook cover — copyright and impersonation risk.
  - [ ] Square image, at least **512 × 512 px** (1024 × 1024 is better).
  - [ ] Readable at 40 px: test by zooming out — if "EVD" is unreadable,
        simplify further. No small print, no tagline in the image.
  - [ ] High contrast, one background colour, no photo background.
  - [ ] Set it: channel → Edit → **Channel Photo** → upload.
- [ ] **Channel type:** Public (so it is discoverable in Telegram search and
      shareable by link). The username is now confirmed
      (@learnvocabularydaily), so this step is no longer blocked on
      username confirmation.
- [ ] **Username:** confirmed as `@learnvocabularydaily`
      (https://t.me/learnvocabularydaily) — no placeholder remains in this
      file. If the username ever changes, update this file, `README.md`,
      and every post that links the channel.

---

## 3. Pinned welcome post (pin this first)

Post this from the **channel owner's account** (not the bot), then pin it.
Pin: long-press the message → **Pin**. Keep it pinned permanently — it is
the first thing a new subscriber sees.

> 📚 **Welcome to English Vocabulary Daily!**
>
> One new English word every morning, one quiz every evening. Free, 2 minutes a day — that's all it takes.
>
> **🗓️ How it works**
> 🌅 **07:15 UTC — Word of the Day:** one word, its pronunciation, its
> meaning, an example sentence, and synonyms.
> 🧠 **17:15 UTC — Evening Quiz:** a 4-option quiz on the morning word,
> plus yesterday's answer.
> 💬 **Friday:** Phrasal Verb Friday.
> 🗣️ **Saturday:** Idiom Saturday.
>
> **🚀 Start today — Day 1**
> You don't need to catch up. Day 1 starts the day you join: read today's
> word, try the quiz tonight, and write your own sentence with the word in
> the comments — that's how the word sticks. No homework, no test, no
> pressure.
>
> **🔒 Stay safe — please read**
> We never DM first, and we never ask for money in DM. The only paid thing
> we will ever offer is announced here in this channel, in a pinned post.
> If anyone messages you pretending to be us, asking for payment, a code,
> or your account details — it is a scam. Block and report them.
>
> Free forever. One word a day. See you tomorrow morning. 📖

Checklist:

- [ ] Posted from the owner's account (not the bot).
- [ ] Pinned, and the pin is visible at the top of the channel.
- [ ] The anti-scam lines are present word-for-word — do not shorten them.

---

## 4. Pinned sales post — Stars PDF (pin this second)

Post this from the **owner's account**, then pin it below the welcome post.
Do **not** post it before the channel has real content (see §5) — a sales
post in an empty channel kills trust. Earliest sensible time: end of Week 1,
once 7 word+quiz pairs are live.

> 📕 **365 Words + Quiz — the complete PDF**
>
> Every word from this channel, in one book you can keep forever.
>
> **What's inside:**
> ✅ **365 words** — one for every day of the year, with meaning,
> pronunciation, example sentence, and synonyms
> ✅ **1,095 quiz questions** — 3 questions for every word, so you actually
> remember them
> ✅ **12 review pages** — one monthly review to test yourself and track
> your progress
> ✅ **Progress tracker** — tick off each word and watch your vocabulary grow
>
> **Price: 350 Telegram Stars (~$4.55)**
> One payment, yours forever. No subscription.
>
> **How to get it:**
> Tap the button below / follow the link in this post to buy with Stars.
> The PDF is sent to you right after purchase.
>
> **Is it worth it?**
> The daily word and the evening quiz here in the channel are — and always
> will be — **completely free**. The PDF is only for people who want
> everything in one place, offline, with the extra quizzes and the tracker.
> No pressure either way. Keep learning free here. 📚
>
> *Questions? Ask in the comments of this post — we answer here in the
> channel, never in DM.*

Checklist:

- [ ] Posted only after 7 days of real content are live.
- [ ] Price is exactly **350 Stars (~$4.55)** — do not discount it in Week 1.
- [ ] The "daily posts are free" lines are present — never imply the
      free posts will stop.
- [ ] The buy button/link actually works (test it with a second account
      before pinning). If Stars payments are not set up yet, **do not post
      this** — set up the Stars product first, then post.
- [ ] Pinned second, under the welcome post.

**Income honesty (for the owner, not for subscribers):** at ~10,000 members
this channel realistically earns **$65–245/month**; $200–1,000/month needs
~20,000–50,000 members. Telegram Ads only after 1,000 members. Never quote
the higher range as a near-term expectation.

---

## 5. First 7 days — backup posts plan (channel must not be empty)

**Purpose:** nobody joins an empty channel. Post these 7 word+quiz pairs
**before inviting anyone**. Post each word in the morning and its quiz the
same evening, mirroring the 07:15 / 17:15 UTC rhythm.

**Words (by word only):** drawn from the **first 30 entries of
`data/lessons.json`**, in bank order. Note: `lessons.json` carries **no CEFR
level field**, so "first 30 A1 lessons" here means the first 30 entries of
the bank as stored — the words below are exactly entries 1–7 of that list.
Do not re-order them; the automation picks words in the same bank order.

| Day | Word (morning, 07:15 UTC) | Quiz (evening, 17:15 UTC) |
|-----|---------------------------|---------------------------|
| Day 1 | **abandon** | Quiz on *abandon* |
| Day 2 | **ability** | Quiz on *ability* |
| Day 3 | **absent** | Quiz on *absent* |
| Day 4 | **absolute** | Quiz on *absolute* |
| Day 5 | **absorb** | Quiz on *absorb* |
| Day 6 | **abundant** | Quiz on *abundant* |
| Day 7 | **accept** | Quiz on *accept* |

**How to post them — pick one method, do not mix both:**

- **Method A (recommended): run the automation.** Once Secrets are set and
  the repo is pushed, the scheduled workflow posts the word and quiz
  automatically each day. The automation's word is chosen by day-of-year,
  not by this table — so the words it posts will **not** be abandon/ability/
  absent on those dates. That is fine: the table above is the *backup plan
  for content*, not a promise of which word lands on which date. If exact
  Day 1 = abandon matters, use Method B.
- **Method B (exact words): post manually.** Copy each word's meaning,
  phonetic, example, synonyms, and quiz from the bank (or from a local
  dry-run: `python3 scripts/post.py` prints the message without sending)
  and post it yourself from the owner's account, morning + evening, for
  7 days. Add "Day N/365" to the top of each manual post by hand — the
  template does not add it yet (see the gap note at the top of this file).
  Only after Day 7, switch the automation on.

**Rules for the 7 days:**

- [ ] Day 1 word + Day 1 quiz posted before any invite is sent.
- [ ] Every post carries its **Day N/365** label (by hand if Method B).
- [ ] Do not post all 7 days' words in one burst — one word per morning,
      one quiz per evening. A channel with 14 posts timestamped in the same
      hour looks automated and empty at the same time.
- [ ] Do not invite anyone until Day 3 at the earliest, and ideally Day 7.
- [ ] Phrasal Verb Friday / Idiom Saturday: if Day 6 or 7 falls on a
      Friday/Saturday, post the themed word manually that day (see §6) —
      the automation will not do it for you.

---

## 6. Weekly rhythm after launch

| Day | Morning (07:15 UTC) | Evening (17:15 UTC) |
|-----|---------------------|---------------------|
| Monday–Thursday | Word of the Day | Quiz on the morning word |
| **Friday** | **Phrasal Verb Friday** — one phrasal verb (meaning + example + quiz in the evening) | Quiz on the phrasal verb |
| **Saturday** | **Idiom Saturday** — one idiom (meaning + example + quiz in the evening) | Quiz on the idiom |
| Sunday | Word of the Day | Quiz on the morning word |

- [ ] Until the poster is updated to handle Friday/Saturday themes, the
      owner posts the Friday phrasal verb and Saturday idiom **manually**
      (same format as a normal word post, labelled "Phrasal Verb Friday" /
      "Idiom Saturday").
- [ ] Never skip a day in the first 30 days — consistency is the retention
      mechanism. If a run fails, check `logs/error-log.md` and re-run the
      workflow manually the same day (see `BOT_COMMANDS.md` §4).

---

## 7. Growth plan — Weeks 1–4

**Targets (realistic, not guaranteed):** 300–600 members in 4 weeks;
1,000 members in 8–12 weeks. Growth is slow at first — the first 100 are
the hardest. Never promise a faster number.

### Week 1 — Foundation (Days 1–7). Target: first 20–50 members.

- [ ] Days 1–7 backup posts live (§5). Nothing else until they are.
- [ ] Welcome post pinned (§3). Bio + photo applied (§2).
- [ ] Invite **acquaintances only** — friends, family, classmates, people
      who know the owner personally and would genuinely want an English
      word a day. Personal message, one by one, no broadcast list.
- [ ] Cap: **200 manual invites total, ever** — Telegram limits how many
      people can be added, and mass-adding strangers gets the account
      restricted. Stay far below the cap in Week 1 (aim for 20–50 adds).
- [ ] Start posting on **X daily**: one short post per day — today's word +
      one example sentence + channel link. No hashtags spam (max 2–3).
- [ ] No Reddit yet in Week 1 (channel is too new — see Week 2).

### Week 2 — First outside traffic. Target: 50–150 members.

- [ ] Keep X daily (same format, every day without fail).
- [ ] **Reddit 2–3× per week** — only in subreddits where self-promotion is
      allowed and the post genuinely helps (e.g. r/EnglishLearning):
      share one useful word with a full explanation in the post itself,
      channel link at the end, never a bare link. Read each subreddit's
      rules first; a removed spam post hurts more than no post.
- [ ] Ask the Week 1 members (once, politely, in the channel): "If this
      helped you, forward today's word to one friend learning English."
- [ ] Reply to every comment in the first 2 weeks — early comments are the
      retention signal.

### Week 3 — Cross-promotion. Target: 150–350 members.

- [ ] Keep X daily + Reddit 2–3×/week.
- [ ] **Cross-promo with channels of 200–2,000 members** (similar size,
      English-learning or study niche): propose a mutual shout-out — they
      post about this channel once, this channel posts about theirs once.
      Small channels answer; big channels ignore. Contact the admin
      politely, once, in their channel's contact route — never by cold DM
      spam.
- [ ] Pin the Stars PDF sales post (§4) at the end of Week 3, once 3 weeks
      of content are visible.

### Week 4 — Consolidate. Target: 300–600 members.

- [ ] Keep X daily + Reddit 2–3×/week + 1–2 cross-promos.
- [ ] Review: which X posts got clicks, which Reddit posts survived, which
      word posts got comments. Do more of what worked; drop what did not.
- [ ] If under 100 members at end of Week 4: the problem is distribution,
      not content — increase X/Reddit quality (full explanations in the
      post, not just a link) before trying anything new.

### Never — the hard rules

- [ ] **NEVER buy members.** Bought members are bots/dead accounts: they
      destroy engagement rate, risk a Telegram ban, and advertisers can
      tell. Zero exceptions.
- [ ] **NEVER mass-invite.** No adding strangers, no scraping usernames,
      no bulk adds. Acquaintances only, cap 200, one by one.
- [ ] **NEVER cold DM** strangers to promote the channel. It is spam, it
      gets reported, and it gets the account restricted.
- [ ] **NEVER promise income** to subscribers or to the owner ("you will
      earn $X"). The honest range is in §4.
- [ ] **NEVER copy content** from BBC, Duolingo, textbooks, or other
      channels. All examples are original to this repo.

---

## 8. Setup checklist — DONE vs OPEN

Mark DONE only for what is verified (live read, run log, or commit).
Last reviewed 2026-11-22.

| # | Item | Status | Evidence / note |
|---|------|--------|-----------------|
| 1 | Channel built ("English Vocabulary Daily") | ✅ DONE | User built it; username confirmed 20 Nov 2026: @learnvocabularydaily (https://t.me/learnvocabularydaily), channel ID -1004348347589 |
| 2 | Bot made admin in the channel | ✅ DONE | Verified 20 Nov 2026 via getChatMember: bot is admin with can_post_messages, can_edit_messages, can_delete_messages, can_manage_chat, can_change_info all true; can_promote_members false |
| 3 | Exact channel username confirmed | ✅ DONE | Confirmed 20 Nov 2026: @learnvocabularydaily — https://t.me/learnvocabularydaily, channel ID -1004348347589 |
| 4 | Bot admin permissions verified via API | ✅ DONE | Verified 20 Nov 2026 via getChatMember (see row 2). Note: the bot holds post/edit/delete/manage/change-info — not "Post Messages only" (the old least-privilege plan was superseded; see docs/channel-setup-guide.md) |
| 5 | Channel name set to "English Vocabulary Daily" | ✅ DONE | Verified 20 Nov 2026 via getChat |
| 6 | Bio applied verbatim (164 chars) | ✅ DONE | Verified 20 Nov 2026 via getChat — exact 164-char bio |
| 7 | Channel photo applied (EVD logo) | ✅ DONE | Verified 20 Nov 2026 via getChat — photo set |
| 8 | Channel set to Public | ✅ DONE | Public username @learnvocabularydaily live since 20 Nov 2026 (https://t.me/learnvocabularydaily) |
| 9 | Pinned welcome post posted + pinned | ✅ DONE | Posted + pinned 20 Nov 2026, message_id 5, verified via getChat |
| 10 | First 7 days of backup posts live | ⬜ OPEN | Only 2 days of posts exist (20–21 Nov) and the word for 325 never posted — 7 backup days are not live yet |
| 11 | GitHub repo pushed (public) | ✅ DONE | Repo halakouai-byte/english-vocab-daily public since 20 Nov 2026; HEAD 6a75bef (watchdog package, 21 Nov) |
| 12 | GitHub Secrets set (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`) | ✅ DONE | Set by the owner; proven by three live posts (manual run #1, scheduled run #2, manual run #3) — 20–21 Nov 2026 |
| 13 | First live post via workflow succeeds | ✅ DONE | Manual run #1 posted lesson 324 "fill" 20 Nov 2026 16:29 Tehran; scheduled run #2 posted the quiz the same evening |
| 14 | Dedupe proof (second same-kind run posts nothing) | ✅ DONE | Runs #4 (21 Nov, 18s) and #5 (21 Nov ~22:10 UTC, 10s) both logged "Duplicate detected — skipping send."; state.json unchanged |
| 15 | Pinned Stars PDF sales post (350 Stars) | ⬜ OPEN | Not built yet — earliest after 7 days of real content (§4) |
| 16 | "Day N/365" added to post templates | ✅ DONE | Added 22 Nov 2026: word template carries `🗓️ *Day {day}/365*`; poll question carries `Day {day}/365: …` |
| 17 | Friday/Saturday themes automated or manual routine set | ⬜ OPEN | Manual until the poster is updated (§6) — Phrasal Verb Friday + Idiom Saturday not posted yet |
| 18 | Week 1 growth started (acquaintances only, cap 200) | ⬜ OPEN | Only after row 10 — §7 |
| 19 | Evening quiz is a Telegram Poll | ✅ DONE | Added 22 Nov 2026: `sendPoll` (type=quiz, correct_option_id, explanation = yesterday's answer) |

**Summary: 15 DONE · 4 OPEN (rows 10, 15, 17, 18).**

**What is still open:**

1. **7 backup days** (row 10) — post the missing days before inviting anyone (§5).
2. **Stars PDF sales post** (row 15) — after 7 days of real content (§4).
3. **Friday/Saturday themes** (row 17) — manual routine or poster update (§6).
4. **Week 1 growth** (row 18) — only after row 10 (§7).
