import requests
import json

def fetch_match_data(match_id):
    """Fetch match data from OpenDota API."""
    url = f"https://api.opendota.com/api/matches/{match_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching match data: {e}")
        return None

def load_hero_data(json_path="heroes.json"):
    """Load both localized and NPC-style hero names from heroes.json."""
    with open(json_path, "r", encoding="utf-8") as f:
        hero_data = json.load(f)
    id_to_localized = {int(info["id"]): info["localized_name"] for info in hero_data.values()}
    id_to_npc = {int(info["id"]): info["name"] for info in hero_data.values()}
    npc_to_id = {v: int(k) for k, v in id_to_npc.items()}
    return id_to_localized, id_to_npc, npc_to_id

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
    """Determine team based on player slot."""
    return "Radiant" if player_slot < 128 else "Dire"

def get_kills_before_time(kills_log, timestamp):
    """Count how many times this player killed each hero before a given timestamp."""
    kills = {}
    for entry in kills_log:
        if entry["time"] <= timestamp:
            kills[entry["key"]] = kills.get(entry["key"], 0) + 1
    return kills

def get_deaths_before_time(match_data, player_slot, timestamp, npc_name):
    """Count how many times this hero was killed before the given timestamp."""
    deaths = {}
    for player in match_data.get("players", []):
        if player.get("player_slot") == player_slot:
            continue
        for entry in player.get("kills_log", []):
            if entry["time"] <= timestamp and entry["key"] == npc_name:
                hero_id = player.get("hero_id")
                deaths[hero_id] = deaths.get(hero_id, 0) + 1
    return deaths

def get_previous_messages(current_index, chat_log, match_data, hero_names):
    """Collect readable previous messages before the current one."""
    context_window = 5
    start = max(0, current_index - context_window)
    previous = []
    for i in range(start, current_index):
        msg = chat_log[i]
        player_slot = msg.get("player_slot")
        hero = get_hero_name_by_slot(match_data, player_slot, hero_names)
        team = get_team_by_slot(player_slot)
        text = msg.get("key", "")
        previous.append(f"{hero} ({team}): {text}")
    return previous

def get_advantage(match_data, timestamp):
    """Get radiant gold and xp advantage at given time in seconds."""
    minute = max(0, min(timestamp // 60, len(match_data.get("radiant_gold_adv", [])) - 1))
    gold_adv = match_data.get("radiant_gold_adv", [0])[minute]
    xp_adv = match_data.get("radiant_xp_adv", [0])[minute]
    return gold_adv, xp_adv

def format_time_mmss(seconds):
    """Format time in MM:SS format."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02}"

def get_context_for_chat_message(index, chat_log, match_data, hero_names, npc_names, npc_to_id):
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
        "msg": message.get("key"),
        "previous_messages": get_previous_messages(index, chat_log, match_data, hero_names),
        "killed_before_time": kills_named,
        "killed_by_before_time": deaths_named,
        "radiant_gold_adv": gold_adv,
        "radiant_xp_adv": xp_adv,
    }

if __name__ == "__main__":
    hero_names, npc_names, npc_to_id = load_hero_data("heroes.json")
    match_id = input("Enter Dota 2 match ID: ")
    match_data = fetch_match_data(match_id)

    if match_data:
        chat_log = match_data.get("chat", [])
        print(f"\nMatch ID: {match_data.get('match_id')}")
        print(f"Total Chat Messages: {len(chat_log)}")

        for i, msg in enumerate(chat_log):
            context = get_context_for_chat_message(i, chat_log, match_data, hero_names, npc_names, npc_to_id)
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
