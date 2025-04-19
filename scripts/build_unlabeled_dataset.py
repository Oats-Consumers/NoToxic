import requests
import json
import time
from my_secrets import OPENDOTA_API_KEY
from utils.valid_ids_generator import fetch_valid_ids
from utils.game_info_final import (
    fetch_match_data, request_reparse, load_hero_data, load_chatwheel_data,
    is_valid_message, is_chatwheel_message, get_context_for_chat_message
)

OUTPUT_FILE = "datasets/unlabeled_dataset.jsonl"
MAX_MESSAGES = 150  # Approximate target message count
MATCH_BUFFER = 15   # Extra matches to fetch in case some have no valid messages

def collect_contexts_from_match(match_id, hero_names, npc_names, npc_to_id, chatwheel_data):
    match_data = fetch_match_data(match_id)
    chat_log = match_data.get("chat") if match_data else []

    if not chat_log:
        print(f"No messages for match {match_id}. Requesting reparse.")
        request_reparse(match_id)
        for retry in range(20):
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
            continue  # Skip Chat Wheel messages from the final dataset
        contexts.append(context)

    print(f"✔ Parsed {len(contexts)} valid messages from match {match_id}")
    return contexts

if __name__ == "__main__":
    print("Loading heroes and chat wheel data...")
    hero_names, npc_names, npc_to_id = load_hero_data("data/heroes.json")
    chatwheel_data = load_chatwheel_data("data/chat_wheel.json")

    print("Fetching valid match IDs...")
    match_ids = fetch_valid_ids(target_count=MATCH_BUFFER)

    dataset = []
    for match_id in match_ids:
        if len(dataset) >= MAX_MESSAGES:
            break
        contexts = collect_contexts_from_match(match_id, hero_names, npc_names, npc_to_id, chatwheel_data)
        dataset.extend(contexts)

    dataset = dataset[:MAX_MESSAGES]
    print(f"\n💾 Saving {len(dataset)} messages to {OUTPUT_FILE}...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for item in dataset:
            json.dump(item, f)
            f.write("\n")

    print("✅ Done.")
