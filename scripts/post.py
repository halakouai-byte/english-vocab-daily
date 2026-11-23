#!/usr/bin/env python3
"""
English Vocabulary Daily — Telegram poster.
No AI at runtime. Only Python stdlib + requests.
Deterministic: word = lessons[day_of_year % len(lessons)].

Behaviour:
- Morning run (UTC hour < 12, cron 07:15 UTC): Word of the Day.
- Evening run (UTC hour >= 12, cron 17:15 UTC): Telegram Poll quiz on the
  morning word (question "Day {day}/365: {quiz_q}", 4 options,
  correct_option_id = index of quiz_a, explanation = yesterday's answer).
- POST_KIND env can force "word" or "quiz" (for manual runs).
- Dedupe: SHA-256 of the rendered message (word) or the canonical poll
  payload (quiz) is stored in data/state.json. If the hash matches
  last_hash, nothing is sent.
- Race guard: just before sending, post.py re-reads the LIVE state.json
  from main (raw.githubusercontent.com, public repo, no auth) and skips
  if it already records this post (same hash) or today's slot with the
  same kind. Two runs starting in the same minute both read the same
  checked-out state and both pass the local dedupe (22 Nov 2026: the word
  posted twice, messages 11 and 12; 20 Nov 2026: the "fill" quiz posted
  twice, messages 8 and 9). Fail-open: an unreadable live state means
  "proceed" — never block a post on it. Residual window: the seconds
  between the other run's send and its state push.
- Retry: exponential backoff (1s, 2s, 4s, 8s, 16s) on network/5xx errors.
  If Telegram returns 429, respect retry_after and wait, then retry once.
- Enrichment (optional, never required): Free Dictionary API
  (https://api.dictionaryapi.dev/api/v2/entries/en/<word>, no key).
  Any failure -> fall back to the bank lesson. Never post broken content.
- Dry-run: if TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is missing,
  print the message (word) or the poll payload (quiz) instead of sending
  and exit 0. This is how you test locally without a token.
- State: updates data/state.json {last_index, last_date, last_hash, last_kind}
  after a successful send (or dry-run, with hash recorded only on real send
  -- dry-run does NOT update state, so a real run is not skipped).
- Errors are appended to logs/error-log.md and also printed.
"""
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import requests

try:
    from templates import WORD_TEMPLATE
except ImportError:  # when run as scripts/post.py from repo root
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from templates import WORD_TEMPLATE

BASE = Path(__file__).resolve().parent.parent
LESSONS_FILE = BASE / "data" / "lessons.json"
STATE_FILE = BASE / "data" / "state.json"
LOG_FILE = BASE / "logs" / "error-log.md"

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
POST_KIND = os.environ.get("POST_KIND", "").strip().lower()  # "word" | "quiz" | ""

# Race guard: the live state.json on main, re-read just before sending.
# Public repo, no auth needed. See fetch_live_state().
LIVE_STATE_URL = "https://raw.githubusercontent.com/halakouai-byte/english-vocab-daily/main/data/state.json"

# The token is embedded in the Telegram API URL (api.telegram.org/bot<TOKEN>/...).
# requests/urllib3 network exceptions can include that URL in their message,
# so any error text must be redacted BEFORE it is logged or printed —
# logs/error-log.md is committed back to the (public) repo by post.yml.
_TOKEN_RE = re.compile(r"bot\d+:[A-Za-z0-9_-]{35}")


def _redact(text: str) -> str:
    if BOT_TOKEN:
        text = text.replace(BOT_TOKEN, "[REDACTED]")
    return _TOKEN_RE.sub("bot[REDACTED]", text)


def escape_markdown(text) -> str:
    """Escape Telegram legacy-Markdown specials in bank/enrichment content.

    Template markup (*bold* etc.) lives in templates.py and is NOT escaped;
    only interpolated lesson fields go through this, so a future word,
    meaning or phonetic containing *, _, `, [ or ] cannot break formatting
    or inject markup. Current bank contains none of these characters, so
    output for existing lessons is unchanged.
    """
    return re.sub(r"([\\*_`\[\]])", r"\\\1", str(text))


def log_error(msg: str) -> None:
    msg = _redact(str(msg))
    line = f"- {datetime.now(timezone.utc).isoformat()} {msg}\n"
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass
    print(f"ERROR: {msg}", file=sys.stderr)


def load_lessons():
    try:
        lessons = json.loads(LESSONS_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        log_error(f"failed to load lessons.json: {e}")
        raise SystemExit(1)
    if not isinstance(lessons, list) or len(lessons) < 365:
        log_error(f"lessons.json invalid: expected >=365 lessons, got {len(lessons) if isinstance(lessons, list) else 'not-a-list'}")
        raise SystemExit(1)
    for i, lesson in enumerate(lessons):
        for field in ("word", "meaning", "phonetic", "example", "synonyms", "quiz_q", "quiz_options", "quiz_a"):
            if field not in lesson or lesson[field] in ("", [], None):
                log_error(f"lesson {i} ({lesson.get('word')}) missing/empty field: {field}")
                raise SystemExit(1)
        if len(lesson["quiz_options"]) != 4 or lesson["quiz_a"] not in lesson["quiz_options"]:
            log_error(f"lesson {i} ({lesson.get('word')}) bad quiz options")
            raise SystemExit(1)
    return lessons


def load_state():
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return {
            "last_index": int(state.get("last_index", -1)),
            "last_date": str(state.get("last_date", "")),
            "last_hash": str(state.get("last_hash", "")),
        }
    except Exception as e:
        log_error(f"state.json unreadable, starting fresh: {e}")
        return {"last_index": -1, "last_date": "", "last_hash": ""}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fetch_live_state():
    """Re-read state.json from main (public raw URL, no auth).

    Returns the live state dict, or None when it cannot be read (network
    error, bad JSON, unexpected shape). None means "proceed" — the race
    guard is fail-open by design: an unreadable live state must never
    block a post. Used only in main(), just before sending.
    """
    try:
        req = urllib.request.Request(
            LIVE_STATE_URL, headers={"User-Agent": "EnglishVocabularyDaily/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            live = json.loads(resp.read().decode("utf-8"))
        if not isinstance(live, dict):
            return None
        return {
            "last_index": int(live.get("last_index", -1)),
            "last_date": str(live.get("last_date", "")),
            "last_hash": str(live.get("last_hash", "")),
            "last_kind": str(live.get("last_kind", "")),
        }
    except Exception as e:
        print(f"Race guard: live state unreadable ({_redact(str(e))}) — proceeding with checked-out state.")
        return None


def enrich_from_dictionary(word: str, lesson: dict) -> dict:
    """Optional enrichment only. Returns lesson unchanged on any failure."""
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(word)}"
        req = urllib.request.Request(url, headers={"User-Agent": "EnglishVocabularyDaily/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        # Only accept a clean, single definition; never replace the bank meaning
        # with something broken. We only add a phonetic if the bank one is empty.
        if isinstance(data, list) and data and isinstance(data[0], dict):
            phon = data[0].get("phonetic") or ""
            if phon and not lesson.get("phonetic"):
                lesson = dict(lesson)
                lesson["phonetic"] = phon
    except Exception as e:
        # Enrichment failure is not fatal — fall back to the bank.
        print(f"Enrichment skipped for {word!r}: {_redact(str(e))}")
    return lesson


def render_word(lesson: dict, day: int) -> str:
    return WORD_TEMPLATE.format(
        word=escape_markdown(lesson["word"]),
        day=day,
        phonetic=escape_markdown(lesson["phonetic"]),
        meaning=escape_markdown(lesson["meaning"]),
        example=escape_markdown(lesson["example"]),
        synonyms=", ".join(escape_markdown(s) for s in lesson["synonyms"]),
    )


def build_poll(lesson: dict, yesterday: dict | None, day: int) -> dict:
    """Build the evening quiz as a Telegram Poll payload.

    Poll question/options are plain text (no Markdown). The day label goes
    at the start of the question. Explanation is yesterday's answer, cut to
    Telegram's 200-character limit.
    """
    opts = [str(o) for o in lesson["quiz_options"]]
    question = f"Day {day}/365: {lesson['quiz_q']}"[:300]
    explanation = ""
    if yesterday:
        explanation = (
            f"Yesterday's answer: {yesterday['word']} — {yesterday['meaning']}"
        )[:200]
    payload = {
        "question": question,
        "options": opts,
        "correct_option_id": opts.index(lesson["quiz_a"]),
        "type": "quiz",
    }
    if explanation:
        payload["explanation"] = explanation
    return payload


def send_message(text: str) -> bool:
    """Send one message. Returns True on success. Retries with backoff."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    delays = [1, 2, 4, 8, 16]
    for attempt in range(len(delays) + 1):
        try:
            resp = requests.post(url, json=payload, timeout=30)
        except requests.RequestException as e:
            if attempt < len(delays):
                time.sleep(delays[attempt])
                continue
            log_error(f"sendMessage network error after retries: {e}")
            return False
        if resp.status_code == 200:
            return True
        # Respect Telegram rate limiting
        if resp.status_code == 429:
            try:
                wait = int(resp.json().get("parameters", {}).get("retry_after", 30))
            except Exception:
                wait = 30
            wait = min(max(wait, 1), 120)
            print(f"Rate limited (429), waiting {wait}s")
            time.sleep(wait)
            # one retry after waiting
            try:
                resp2 = requests.post(url, json=payload, timeout=30)
                if resp2.status_code == 200:
                    return True
            except requests.RequestException as e:
                log_error(f"sendMessage retry after 429 failed: {e}")
            log_error(f"sendMessage failed after 429: {resp.text[:500]}")
            return False
        if resp.status_code >= 500 and attempt < len(delays):
            time.sleep(delays[attempt])
            continue
        log_error(f"sendMessage failed HTTP {resp.status_code}: {resp.text[:500]}")
        return False
    return False


def send_poll(payload: dict) -> bool:
    """Send the evening quiz as a Telegram Poll. Returns True on success.

    Mirrors send_message (same retries/backoff/429 handling) but posts to
    sendPoll with type=quiz. Poll questions/options are plain text.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPoll"
    body = {"chat_id": CHAT_ID, **payload}
    delays = [1, 2, 4, 8, 16]
    for attempt in range(len(delays) + 1):
        try:
            resp = requests.post(url, json=body, timeout=30)
        except requests.RequestException as e:
            if attempt < len(delays):
                time.sleep(delays[attempt])
                continue
            log_error(f"sendPoll network error after retries: {e}")
            return False
        if resp.status_code == 200:
            return True
        # Respect Telegram rate limiting
        if resp.status_code == 429:
            try:
                wait = int(resp.json().get("parameters", {}).get("retry_after", 30))
            except Exception:
                wait = 30
            wait = min(max(wait, 1), 120)
            print(f"Rate limited (429), waiting {wait}s")
            time.sleep(wait)
            # one retry after waiting
            try:
                resp2 = requests.post(url, json=body, timeout=30)
                if resp2.status_code == 200:
                    return True
            except requests.RequestException as e:
                log_error(f"sendPoll retry after 429 failed: {e}")
            log_error(f"sendPoll failed after 429: {resp.text[:500]}")
            return False
        if resp.status_code >= 500 and attempt < len(delays):
            time.sleep(delays[attempt])
            continue
        log_error(f"sendPoll failed HTTP {resp.status_code}: {resp.text[:500]}")
        return False
    return False


def main() -> int:
    now = datetime.now(timezone.utc)
    lessons = load_lessons()
    state = load_state()

    day_of_year = now.timetuple().tm_yday
    index = day_of_year % len(lessons)
    lesson = enrich_from_dictionary(lessons[index]["word"], lessons[index])

    if POST_KIND in ("word", "quiz"):
        kind = POST_KIND
    else:
        kind = "word" if now.hour < 12 else "quiz"

    poll = None
    text = None
    if kind == "word":
        text = render_word(lesson, day_of_year)
    else:
        # Day 1: no word has been posted yet, so there is no yesterday's
        # answer. Previously prev_index wrapped to lessons[-1] and the quiz
        # revealed a word that was never posted. Show "—" instead.
        if state.get("last_index", -1) < 0:
            yesterday = None
        else:
            prev_index = (index - 1) % len(lessons)
            yesterday = lessons[prev_index]
        poll = build_poll(lesson, yesterday, day_of_year)

    if text is not None and not text.strip():
        log_error("rendered message is empty — refusing to post broken content")
        return 1
    if poll is not None and (not poll["question"].strip() or not poll["options"]):
        log_error("poll payload is empty — refusing to post broken content")
        return 1

    # Dedupe: word posts hash the rendered text; quiz polls hash the
    # canonical poll payload (question + options + correct answer).
    if text is not None:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    else:
        digest = hashlib.sha256(
            json.dumps(poll, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()
    if digest == state.get("last_hash"):
        print("Duplicate detected (same hash as last post) — skipping send.")
        return 0

    if not BOT_TOKEN or not CHAT_ID:
        print("=== DRY RUN (no TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID set) ===")
        if text is not None:
            print(text)
        else:
            print("POLL:")
            print(json.dumps(poll, ensure_ascii=False, indent=2))
        print("=== END DRY RUN — nothing sent, state not updated ===")
        return 0

    # Race guard: re-read the LIVE state.json from main just before
    # sending. Two runs starting in the same minute both read the same
    # checked-out state and both pass the local dedupe above (22 Nov 2026:
    # the word posted twice; 20 Nov 2026: the "fill" quiz posted twice).
    # If main already records this exact post (same hash) — or today's
    # slot with the same kind — skip. Fail-open: an unreadable live state
    # means "proceed" (see fetch_live_state). Residual window: the seconds
    # between the other run's send and its state push.
    live = fetch_live_state()
    if live is not None:
        if digest == live.get("last_hash"):
            print("Race guard: live state already has this post — skipping send.")
            return 0
        if live.get("last_date") == now.date().isoformat() and live.get("last_kind") == kind:
            print(f"Race guard: live state already has today's {kind} — skipping send.")
            return 0

    if text is not None:
        ok = send_message(text)
    else:
        ok = send_poll(poll)
    if not ok:
        return 1

    state["last_index"] = index
    state["last_date"] = now.date().isoformat()
    state["last_kind"] = kind
    state["last_hash"] = digest
    save_state(state)
    print(f"Posted {kind} for index {index} ({lesson['word']}) at {now.isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
