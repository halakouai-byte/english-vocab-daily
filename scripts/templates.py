"""Fixed, deterministic message templates. No AI, no generation at runtime."""

WORD_TEMPLATE = """📌 *Word of the Day — {word}*
{phonetic}

📖 *Meaning:*
{meaning}

💬 *Example:*
{example}

🔁 *Synonyms:* {synonyms}

✏️ Try it: write your own sentence with *{word}* in the comments.
📚 English Vocabulary Daily — one word every day, free daily word."""

QUIZ_TEMPLATE = """🧠 *Evening Quiz*

{quiz_q}

A) {opt0}
B) {opt1}
C) {opt2}
D) {opt3}

✅ *Yesterday's answer:* {yesterday_word} — {yesterday_meaning}

📚 English Vocabulary Daily — learn one word a day, keep it forever."""
