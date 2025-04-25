import sys, os

from clients import OPEN_DOTA_CLIENT

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
import json
import time
import re
import atexit
from utils.language_check import is_english, save_cache
atexit.register(save_cache)

# Precompiled regex to detect private-use Unicode (e.g., emojis like \ue128)
PRIVATE_USE_REGEX = re.compile(r'[\uE000-\uF8FF]')
LATIN_CHAR_RE = re.compile(r'^[\x00-\x7F]+$')

def fetch_match_data(match_id):
    try:
        return OPEN_DOTA_CLIENT.get_match_details(match_id)
    except requests.RequestException as e:
        print(f"Error fetching match data: {e}")
        return None

def request_reparse(match_id):
    try:
        response = OPEN_DOTA_CLIENT.reparse_match(match_id)
        if response.status_code == 200:
            print(f"Reparse requested for match {match_id}. Waiting for reparse to complete...")
        else:
            print(f"Failed to request reparse (status code {response.status_code}).")
    except requests.RequestException as e:
        print(f"Error requesting reparse: {e}")

def load_hero_data(json_path="heroes.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        hero_data = json.load(f)
    id_to_localized = {int(info["id"]): info["localized_name"] for info in hero_data.values()}
    id_to_npc = {int(info["id"]): info["name"] for info in hero_data.values()}
    npc_to_id = {v: int(k) for k, v in id_to_npc.items()}
    return id_to_localized, id_to_npc, npc_to_id

def load_chatwheel_data(json_path="chat_wheel.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_message_text(key, chatwheel):
    if not isinstance(key, str):
        return key

    # Filter out messages with emojis or private-use characters
    if PRIVATE_USE_REGEX.search(key):
        return None  # Considered invalid later

    if key.isdigit() and key in chatwheel:
        entry = chatwheel[key]
        if "message" in entry:
            message = entry["message"].replace("%s1", "A hero")
            return f"<CHAT_WHEEL> {message} </CHAT_WHEEL>"
        elif "image" in entry:
            image_name = entry["image"].split("/")[-1].replace("_", " ").replace(".png", "")
            return f"<CHAT_WHEEL> {image_name} </CHAT_WHEEL>"

    return key

def is_valid_message(msg, chatwheel):
    key = msg.get("key")
    if not isinstance(key, str):
        return False

    # Exclude emoji/unicode
    if PRIVATE_USE_REGEX.search(key):
        return False

    # Exclude chat wheel IDs unless recognized
    if key.isdigit():
        return key in chatwheel

    # Only allow pure ASCII (no non-English alphabets)
    if not LATIN_CHAR_RE.fullmatch(key.strip()):
        return False

    # Filter out non-English messages using GPT + cache
    if not is_english(key.strip()):
        print(f"🌐 Skipping non-English message: {key}")
        return False

    return True


def is_chatwheel_message(msg, chatwheel):
    key = msg.get("key")
    return isinstance(key, str) and key.isdigit() and key in chatwheel

def get_player_by_slot(match_data, player_slot):
    for player in match_data.get("players", []):
        if player.get("player_slot") == player_slot:
            return player
    return None

def get_hero_id_by_slot(match_data, player_slot):
    player = get_player_by_slot(match_data, player_slot)
    return player.get("hero_id") if player else None

def get_hero_name_by_slot(match_data, player_slot, hero_names):
    hero_id = get_hero_id_by_slot(match_data, player_slot)
    return hero_names.get(hero_id, f"Unknown ({hero_id})")

def get_team_by_slot(player_slot):
    return "Radiant" if player_slot < 128 else "Dire"

def get_kills_before_time(kills_log, timestamp):
    kills = {}
    for entry in kills_log:
        if entry["time"] <= timestamp:
            kills[entry["key"]] = kills.get(entry["key"], 0) + 1
    return kills

def get_deaths_before_time(match_data, player_slot, timestamp, npc_name):
    deaths = {}
    for player in match_data.get("players", []):
        if player.get("player_slot") == player_slot:
            continue
        for entry in player.get("kills_log", []):
            if entry["time"] <= timestamp and entry["key"] == npc_name:
                hero_id = player.get("hero_id")
                deaths[hero_id] = deaths.get(hero_id, 0) + 1
    return deaths

def get_previous_messages(current_index, chat_log, match_data, hero_names, chatwheel):
    context_window = 500
    start = max(0, current_index - context_window)
    previous = []
    for i in range(start, current_index):
        msg = chat_log[i]

        # Skip chat wheel messages for previous messages context (but keep parsing logic)
        if is_chatwheel_message(msg, chatwheel):
            continue

        player_slot = msg.get("player_slot")
        hero = get_hero_name_by_slot(match_data, player_slot, hero_names)
        team = get_team_by_slot(player_slot)
        text = normalize_message_text(msg.get("key", ""), chatwheel)
        previous.append(f"{hero} ({team}): {text}")
    return previous

def get_advantage(match_data, timestamp):
    minute = max(0, min(timestamp // 60, len(match_data.get("radiant_gold_adv", [])) - 1))
    gold_adv = match_data.get("radiant_gold_adv", [0])[minute]
    xp_adv = match_data.get("radiant_xp_adv", [0])[minute]
    return gold_adv, xp_adv

def format_time_mmss(seconds):
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02}"

def get_context_for_chat_message(index, chat_log, match_data, hero_names, npc_names, npc_to_id, chatwheel):
    message = chat_log[index]
    timestamp = message.get("time")
    player_slot = message.get("player_slot")
    hero_name = get_hero_name_by_slot(match_data, player_slot, hero_names)
    npc_name = npc_names.get(get_hero_id_by_slot(match_data, player_slot), "unknown")
    team = get_team_by_slot(player_slot)

    player = get_player_by_slot(match_data, player_slot)
    kills_raw = get_kills_before_time(player.get("kills_log", []), timestamp) if player else {}

    kills_named = {
        hero_names.get(npc_to_id.get(npc, -1), npc): count
        for npc, count in kills_raw.items()
    }

    deaths_raw = get_deaths_before_time(match_data, player_slot, timestamp, npc_name)
    deaths_named = {
        hero_names.get(k, f"Unknown ({k})"): v
        for k, v in deaths_raw.items()
    }

    gold_adv, xp_adv = get_advantage(match_data, timestamp)

    return {
        "time": timestamp,
        "time_str": format_time_mmss(timestamp),
        "hero_name": hero_name,
        "team": team,
        "msg": normalize_message_text(message.get("key"), chatwheel),
        "previous_messages": get_previous_messages(index, chat_log, match_data, hero_names, chatwheel),
        "killed_before_time": kills_named,
        "killed_by_before_time": deaths_named,
        "radiant_gold_adv": gold_adv,
        "radiant_xp_adv": xp_adv,
        "is_chatwheel": is_chatwheel_message(message, chatwheel),
    }

if __name__ == "__main__":
    hero_names, npc_names, npc_to_id = load_hero_data("data/heroes.json")
    chatwheel_data = load_chatwheel_data("data/chat_wheel.json")
    match_id = input("Enter Dota 2 match ID: ")

    # Initial fetch
    match_data = fetch_match_data(match_id)
    chat_log = match_data.get("chat") if match_data else []

    if not chat_log:
        print("No chat messages found. Requesting reparse...")
        request_reparse(match_id)

        print("Waiting for reparse to complete...")
        for retry in range(20):  # Try up to ~5 mins
            time.sleep(15)
            match_data = fetch_match_data(match_id)
            chat_log = match_data.get("chat") if match_data else []
            if chat_log:
                print(f"Reparse completed after {retry+1} tries!")
                break
            print(f"Retry {retry+1}...")

    if not chat_log:
        print("Still no chat data after retries. Exiting.")
        exit()

    chat_log = [msg for msg in chat_log if is_valid_message(msg, chatwheel_data)]

    print(f"\nMatch ID: {match_data.get('match_id')}")
    print(f"Total Valid Chat Messages: {len(chat_log)}")

    for i, msg in enumerate(chat_log):
        context = get_context_for_chat_message(i, chat_log, match_data, hero_names, npc_names, npc_to_id, chatwheel_data)

        if context["is_chatwheel"]:
            continue  # Skip chat wheel messages from being printed/analyzed here

        print("\n--- Chat Message Context ---")
        print(f"Time: {context['time_str']}")
        print(f"Radiant Gold Adv: {context['radiant_gold_adv']}")
        print(f"Radiant XP Adv: {context['radiant_xp_adv']}")
        print("Previous messages:")
        for line in context["previous_messages"]:
            print(f"  {line}")
        print(f"Team: {context['team']}")
        print(f"Hero: {context['hero_name']}")
        print(f"Killed (before msg): {context['killed_before_time']}")
        print(f"Killed By (before msg): {context['killed_by_before_time']}")
        print(f"Message: {context['msg']}")
