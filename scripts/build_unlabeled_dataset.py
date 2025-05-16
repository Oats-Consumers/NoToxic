import json
import time
import os
from utils.valid_ids_generator import fetch_valid_ids
from utils.game_info import (
    fetch_match_data, request_reparse, load_hero_data, load_chatwheel_data,
    is_valid_message, get_context_for_chat_message
)
from tqdm import tqdm

# Config
OUTPUT_FILE = "datasets/unlabeled_dataset.jsonl"
LAST_ID_FILE = "datasets/last_seen_match_id.txt"
MAX_MESSAGES = 10500  # Target total messages (existing + new)
BATCH_SIZE = 1

def load_last_seen_id():
    try:
        with open(LAST_ID_FILE, "r") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return None

def save_last_seen_id(match_id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(str(match_id))

def load_existing_dataset():
    if not os.path.exists(OUTPUT_FILE):
        return []
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def collect_contexts_from_match(match_id, hero_names, npc_names, npc_to_id, chatwheel_data):
    match_data = fetch_match_data(match_id)
    chat_log = match_data.get("chat") if match_data else []

    if not chat_log:
        print(f"No messages for match {match_id}. Requesting reparse.")
        request_reparse(match_id)
        for retry in range(4):
            time.sleep(15)
            match_data = fetch_match_data(match_id)
            chat_log = match_data.get("chat") if match_data else []
            if chat_log:
                print(f"Reparse completed for match {match_id}")
                break
        else:
            print(f"❌ Skipping match {match_id} (no messages)")
            return []

    chat_log = [msg for msg in chat_log if is_valid_message(msg, chatwheel_data)]
    contexts = []

    for i, msg in enumerate(chat_log):
        context = get_context_for_chat_message(i, chat_log, match_data, hero_names, npc_names, npc_to_id, chatwheel_data)
        if context["is_chatwheel"]:
            continue
        contexts.append(context)

    print(f"✔ Parsed {len(contexts)} valid messages from match {match_id}")
    return contexts

if __name__ == "__main__":
    print("Loading heroes and chat wheel data...")
    hero_names, npc_names, npc_to_id = load_hero_data("data/heroes.json")
    chatwheel_data = load_chatwheel_data("data/chat_wheel.json")

    existing_dataset = load_existing_dataset()
    print(f"📂 Loaded {len(existing_dataset)} previously collected messages.")

    last_seen_id = load_last_seen_id()
    dataset = existing_dataset.copy()

    print(f"🔄 Collecting up to {MAX_MESSAGES} messages (total)...")

    with tqdm(total=MAX_MESSAGES, initial=len(dataset), desc="Collecting messages") as progress_bar:
        while len(dataset) < MAX_MESSAGES:
            print(f"\n📥 Fetching next batch of match IDs (after {last_seen_id})...")
            match_ids, last_seen_id = fetch_valid_ids(target_count=BATCH_SIZE, after_match_id=last_seen_id)

            if not match_ids:
                print("⚠️ No more match IDs to process.")
                break

            for match_id in match_ids:
                if len(dataset) >= MAX_MESSAGES:
                    break

                try:
                    contexts = collect_contexts_from_match(match_id, hero_names, npc_names, npc_to_id, chatwheel_data)
                except Exception as e:
                    print(f"❌ Error while processing match {match_id}: {e}")
                    continue

                if not contexts:
                    continue

                with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                    for context in contexts:
                        json.dump(context, f)
                        f.write("\n")
                        dataset.append(context)
                        progress_bar.update(1)

            save_last_seen_id(last_seen_id)
