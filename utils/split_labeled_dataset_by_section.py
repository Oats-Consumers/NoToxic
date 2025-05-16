import json
import csv


INPUT_JSON_PATH = "datasets/labeled_dataset.jsonl"  # adjust if needed
OUTPUT_CSV_PATH = "datasets/processed_dataset.csv"

def format_token(text):
    token_value = text.upper().replace(" ", "_")
    return f"[{token_value}]"

def interpret_advantage(time_str, gold, xp):
    minutes, _ = time_str.split(":")
    min_mark = int(minutes)

    def describe(val, thresholds):
        abs_val = abs(val)
        if abs_val < thresholds[0]:
            return "even"
        elif abs_val < thresholds[1]:
            return "slightly ahead" if val > 0 else "slightly behind"
        elif abs_val < thresholds[2]:
            return "ahead" if val > 0 else "behind"
        else:
            return "dominating" if val > 0 else "being stomped"

    if min_mark < 10:
        gold_thresholds = (500, 1500, 3000)
    elif min_mark < 20:
        gold_thresholds = (1500, 3000, 7000)
    elif min_mark < 30:
        gold_thresholds = (3000, 7000, 10000)
    elif min_mark < 40:
        gold_thresholds = (7000, 10000, 200000)
    elif min_mark < 50:
        gold_thresholds = (10000, 200000, 300000)
    else:
        gold_thresholds = (200000, 300000, 400000)

    if min_mark < 10:
        xp_thresholds = (400, 800, 1600)
    elif min_mark < 20:
        xp_thresholds = (1000, 2000, 4000)
    elif min_mark < 30:
        xp_thresholds = (2000, 4000, 7000)
    else:
        xp_thresholds = (3000, 7000, 15000)

    gold_desc = describe(gold, gold_thresholds)
    xp_desc = describe(xp, xp_thresholds)

    return f"time: {time_str}, radiant_gold_advantage: {format_token(gold_desc)}, radiant_xp_advantage: {format_token(xp_desc)}"


def build_input_string(entry):
    game_state_text = interpret_advantage(entry["time_str"], entry["radiant_gold_adv"], entry["radiant_xp_adv"])
    game_state_str = f"[GAME_STATE] {game_state_text} <SEP>"

    killed_str = "[KILLED] " + " | ".join(
        f"{format_token(hero)}({count})" for hero, count in entry["killed_before_time"].items()
    ) + " <SEP>"

    killed_by_str = "[KILLED_BY] " + " | ".join(
        f"{format_token(hero)}({count})" for hero, count in entry["killed_by_before_time"].items()
    ) + " <SEP>"

    msg_str = f"[MSG] {format_token(entry['hero_name'])} {entry['msg']} {format_token(entry['team'])} <SEP>"

    prev_strs = []
    previous_messages = reversed(entry["previous_messages"])
    for msg in previous_messages:
        hero_team, message = msg.split(":", 1)
        hero, team = hero_team.strip().split(" (")
        team = team.strip(")")
        formatted = f"{format_token(hero)} {format_token(team)}: {message.strip()}"
        prev_strs.append(formatted)

    prev_messages_str = "[PREVIOUS] " + " | ".join(prev_strs)

    return f"{game_state_str} {killed_str} {killed_by_str} {msg_str} {prev_messages_str}"

def get_label(entry):
    return 1 if entry["toxicity"].upper() == "TOXIC" else 0

def process_jsonl_to_csv(input_json_path, output_csv_path, labeling = True):
    processed = []

    with open(input_json_path, "r") as f:
        data = json.load(f)

    for entry in data:
        input_text = build_input_string(entry)
        if labeling:
            label = 1 if entry["toxicity"].upper() == "TOXIC" else 0
            processed.append({
                "input_text": input_text,
                "label": label
            })
        else:
            processed.append({
                "input_text": input_text,
            })

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        if labeling:
            fieldnames = ["input_text", "label"]
        else:
            fieldnames = ["input_text"]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in processed:
            writer.writerow(row)

    print(f"Processed {len(processed)} entries and saved to {output_csv_path}")


if __name__ == "__main__":
    process_jsonl_to_csv(INPUT_JSON_PATH, OUTPUT_CSV_PATH)
