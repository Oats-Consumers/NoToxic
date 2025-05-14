import json
import os
from clients import OPEN_AI_CLIENT, OLLAMA_CLIENT

# Config
MODEL = "gpt-4o"
CACHE_FILE = "datasets/language_cache.json"

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

    is_eng = OLLAMA_CLIENT.check_is_english_text(text)
    language_cache[text] = is_eng
    return is_eng

def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(language_cache, f, ensure_ascii=False, indent=2)
