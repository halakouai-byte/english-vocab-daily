#!/usr/bin/env python3
"""Regenerate data/lessons.json from data/words.txt.

SOURCE OF TRUTH: data/lessons.json itself.
The human-written example sentences in data/lessons.json are the
source of truth and are NEVER overwritten by this script. The old
version of this script rebuilt every example from meta templates
("The word X means ...") and destroyed the fixed bank; those
templates have been deleted on purpose.

What this script does:
- Reads data/words.txt (word|phonetic|meaning|synonyms|type).
- For words already in data/lessons.json: keeps the whole existing
  entry (example, synonyms, quiz, ...) and only updates phonetic /
  meaning / type from words.txt when they changed.
- For words NOT yet in data/lessons.json: creates an entry with
  example set to "" and prints a warning. A human must write a real,
  original example sentence for it before the lesson can be used;
  scripts/post.py must skip entries with an empty example.
- Drops entries whose word is no longer in words.txt.
- Rebuilds quiz distractors deterministically (seed 42) so quizzes
  stay valid after meaning changes.

Run: python3 scripts/generate_lessons.py
"""
import hashlib, json, random, pathlib, sys

BASE = pathlib.Path(__file__).resolve().parent.parent
WORDS_FILE = BASE / "data" / "words.txt"
OUT = BASE / "data" / "lessons.json"

def main():
    lines = [l.strip() for l in WORDS_FILE.read_text(encoding="utf-8").splitlines()
             if l.strip() and not l.strip().startswith("#")]
    words = []
    for line in lines:
        parts = line.split("|")
        if len(parts) != 5:
            raise ValueError(f"Bad line: {line}")
        word, phonetic, meaning, syns, typ = [p.strip() for p in parts]
        words.append({
            "word": word, "phonetic": phonetic, "meaning": meaning,
            "synonyms": [s.strip() for s in syns.split(",") if s.strip()],
            "type": typ,
        })
    seen = set()
    uniq = []
    for e in words:
        k = e["word"].lower()
        if k in seen:
            continue
        seen.add(k)
        uniq.append(e)
    print(f"unique words: {len(uniq)}")

    existing = {}
    if OUT.exists():
        for e in json.loads(OUT.read_text(encoding="utf-8")):
            existing.setdefault(e["word"].lower(), e)

    meanings = [e["meaning"] for e in uniq]
    lessons = []
    missing_examples = []
    for i, e in enumerate(uniq):
        old = existing.get(e["word"].lower())
        if old is not None and old.get("example"):
            # Preserve the human-written example; only sync metadata.
            entry = dict(old)
            entry.update({"phonetic": e["phonetic"], "meaning": e["meaning"],
                          "type": e["type"], "synonyms": e["synonyms"]})
        else:
            if old is None:
                print(f"WARNING: new word with no example yet: {e['word']}")
            else:
                print(f"WARNING: existing entry has no example: {e['word']}")
            missing_examples.append(e["word"])
            entry = {"word": e["word"], "phonetic": e["phonetic"],
                     "meaning": e["meaning"], "example": "",
                     "synonyms": e["synonyms"], "type": e["type"]}
        # Quiz: keep the existing quiz when the meaning did not change
        # and the quiz is still valid; rebuild only when needed, with a
        # per-word deterministic seed so one word's change cannot reshuffle
        # every other lesson's quiz.
        old_quiz_valid = (
            old is not None
            and old.get("meaning") == e["meaning"]
            and old.get("quiz_a") == e["meaning"]
            and len(old.get("quiz_options") or []) == 4
            and len(set(old["quiz_options"])) == 4
            and e["meaning"] in old["quiz_options"]
        )
        if old_quiz_valid:
            entry.update({"quiz_q": old["quiz_q"],
                          "quiz_options": old["quiz_options"],
                          "quiz_a": old["quiz_a"]})
        else:
            wrng = random.Random(
                int(hashlib.sha256(e["word"].encode("utf-8")).hexdigest()[:8], 16))
            pool = [m for j, m in enumerate(meanings) if j != i]
            distractors = wrng.sample(pool, 3)
            options = [e["meaning"]] + distractors
            wrng.shuffle(options)
            if e["type"] == "idiom":
                q = f"What does the idiom \"{e['word']}\" mean?"
            elif e["type"] == "phrasal":
                q = f"What does the phrasal verb \"{e['word']}\" mean?"
            else:
                q = f"What does \"{e['word']}\" mean?"
            entry.update({"quiz_q": q, "quiz_options": options,
                          "quiz_a": e["meaning"]})
        lessons.append(entry)

    OUT.write_text(json.dumps(lessons, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"Wrote {len(lessons)} lessons to {OUT}")
    if missing_examples:
        print(f"NEEDS HUMAN EXAMPLES ({len(missing_examples)}): "
              f"{', '.join(missing_examples)}")
        print("Do NOT publish entries with an empty example.")
        sys.exit(2)

if __name__ == "__main__":
    main()
