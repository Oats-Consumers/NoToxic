from utils.game_info import hero_names
import json

hero_ids = { value : key for key, value in hero_names.items() } # 1 indexed first entry has 1 as a value
hero_ids["npc_dota_lone_druid_bear4"] = 146 # TODO (hotfix, check this later)

for key, value in hero_ids.items():
    print(f"\"[{key.upper().replace(" ", "_")}]\"", end=", \n")

INPUT_JSON_PATH = "datasets/labeled_dataset.jsonl"  # adjust if needed
OUTPUT_METADATA_PATH = "datasets/metadata.jsonl"

def get_team_id(team):
    return 1 if team == 'Radiant' else 2

def get_metadata(entry):
    team = get_team_id(entry['team'])
    team_enemy = 2 if team == 1 else 1
    hero_message = hero_ids[entry['hero_name']]

    # All tokens in [GAME_STATE] → neutral
    game_state_metadata = {
        "team": 0,        # neutral
        "hero_id": 0,     # neutral
        "is_context": 1   # context
    }

    killed_metadata = []
    for hero in entry["killed_before_time"].keys():
        if hero.startswith("npc_dota_lone_druid_bear"):
            continue
        killed_metadata.append({
            "hero_id": hero_ids[hero],
            "team": team_enemy,
            "is_context": 1
        })

    killed_by_metadata = []
    for hero in entry["killed_by_before_time"].keys():
        killed_by_metadata.append({
            "hero_id": hero_ids[hero],
            "team": team_enemy,
            "is_context": 1
        })

    message_metadata = {
        "hero_id": hero_message,
        "team": team,
        "is_context": 2   # target message
    }

    previous_messages_metadata = []
    for msg in entry["previous_messages"]:
        try:
            hero_team, message = msg.split(":", 1)
            hero, msg_team = hero_team.strip().split(" (")
            msg_team = msg_team.strip(")")
            previous_messages_metadata.append({
                "hero_id": hero_ids[hero],
                "team": get_team_id(msg_team),
                "is_context": 1
            })
        except ValueError:
            # fallback → unknown hero/team → neutral
            previous_messages_metadata.append({
                "hero_id": 0,
                "team": 0,
                "is_context": 1
            })

    return {
        "game_state": game_state_metadata,
        "killed": killed_metadata,
        "killed_by": killed_by_metadata,
        "message": message_metadata,
        "previous_messages": previous_messages_metadata
    }

def collect_metadata(input_json_path, output_json_path):
    processed = []
    with open(input_json_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line.strip())
            processed.append(get_metadata(entry))

    with open(output_json_path, "w", encoding="utf-8") as f:
        for row in processed:
            json_str = json.dumps(row)
            f.write(json_str + "\n")

if __name__ == "__main__":
    collect_metadata(INPUT_JSON_PATH, OUTPUT_METADATA_PATH)