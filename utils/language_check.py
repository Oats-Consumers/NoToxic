import json
import os
from openai import OpenAI
from my_secrets import OPENAI_API_KEY

# Config
MODEL = "gpt-4o"
CACHE_FILE = "datasets/language_cache.json"
client = OpenAI(api_key=OPENAI_API_KEY)

# Load cache from disk
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        language_cache = json.load(f)
else:
    language_cache = {}

def is_english(text):
    text = text.strip()
    if text in language_cache:
        return language_cache[text]

    prompt = f"""You're analyzing short in-game chat messages from a Dota 2 match.

Your task: determine whether a message is written in English or not.

- Messages may contain slang, typos, game terms, or symbols like ":)", "??", "b", or "xd".
- Ignore hero names, map calls, or gibberish that appears English-like.
- Do NOT classify short or ambiguous symbols as non-English unless you're certain they belong to another language.
- If you are unsure whether something is another language, assume it is English.
- Many valid English messages are short, chaotic, or emotional — keep that in mind.
- If a message mixes languages, mark it as non-English only if it's mostly non-English.

Examples:
English → "omg techies why"
English → "go mid noob"
English → "gg wp"
English → "lol report"
English → "push bot"
English → "asd fghj"
English → ":)"
English → ":("
English → "b"
English → "Ezi"
English → "?"
English → "x"

Not English → "hola amigo"
Not English → "vamos al mid"
Not English → "el jungla no gankea"
Not English → "por que feed"
Not English → "was machen wir"
Not English → "venite top"
Not English → "io prendo mid"
Not English → "ya nichego ne mogu sdelat"
Not English → "ya picknu carrya"
Not English → "net wardov"

Now evaluate the following message:

Message: "{text}"

Answer with one word only: Yes or No."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        result = response.choices[0].message.content.strip().lower()
        is_eng = result.startswith("yes")
    except Exception as e:
        print(f"⚠️ Language check failed: {e}")
        is_eng = True  # fallback: keep the message

    language_cache[text] = is_eng
    return is_eng

def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(language_cache, f, ensure_ascii=False, indent=2)
