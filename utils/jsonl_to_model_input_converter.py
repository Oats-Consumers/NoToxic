import csv
import json
import argparse
import os


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_INPUT = os.path.join(SCRIPT_DIR, "..", "datasets", "labeled_dataset.jsonl")
DEFAULT_OUTPUT = os.path.join(SCRIPT_DIR, "..", "datasets", "processed_split_toxicity_data.csv")

def interpret_advantage(time, gold, xp):
    (minutes, _) = time.split(":")
    min_mark = int(minutes)

    # threshold_gold based on game phase
    def describe(val, threshold_gold):
        abs_val = abs(val)
        if abs_val < threshold_gold[0]:
            return f"even with the Dire"
        elif abs_val < threshold_gold[1]:
            return "slightly ahead" if val > 0 else "slightly behind"
        elif abs_val < threshold_gold[2]:
            return "ahead" if val > 0 else "behind"
        else:
            return "dominating" if val > 0 else "being stomped"

    if min_mark < 10:
        threshold_gold = (500, 1500, 3000)
    elif min_mark < 20:
        threshold_gold = (1500, 3000, 7000)
    elif min_mark < 30:
        threshold_gold = (3000, 7000, 10000)
    elif min_mark < 40:
        threshold_gold = (7000, 10000, 200000)
    elif min_mark < 50:
        threshold_gold = (10000, 200000, 300000)
    else:
        threshold_gold = (200000, 300000, 400000)

    if min_mark < 10:
        xp_threshold = (400, 800, 1600)
    elif min_mark < 20:
        xp_threshold = (1000, 2000, 4000)
    elif min_mark < 30:
        xp_threshold = (2000, 4000, 7000)
    else:
        xp_threshold = (3000, 7000, 15000)

    gold_adv = describe(gold, threshold_gold)
    xp_adv = describe(xp, xp_threshold)


    winning_gold = f" the Radiant are {gold_adv} in gold"
    winning_exp = f" and the Radiant are {xp_adv} in xp."

    return f"At {time}" + winning_gold + winning_exp

def format_kills(kills_dict, passive="has", active="killed"):
    if not kills_dict:
        return f"{passive} has not {active} any heroes yet."
    entries = [f"{hero} {count} time(s)" for hero, count in kills_dict.items()]
    return f"{passive} {active} " + ", ".join(entries) + "."

def format_chat_as_story(chat_list, speaker=None):
    story_lines = []
    for line in chat_list:
        try:
            name_team, message = line.split(":", 1)
            hero, team = name_team.strip().split(" (")
            team = team.strip(")")
            prefix = f"{hero} from the {team} said EARLIER"
            story_lines.append(f"{prefix}: \"{message.strip()}\"")
        except ValueError:
            # fallback for malformed messages
            story_lines.append(f"A player said: \"{line}\"")
    return "\n".join(story_lines)

def format_message_as_statement(hero_name, team, msg):
    return f'{hero_name} from the {team} NOW says: "{msg}"'

def process_jsonl_to_csv(input_file, output_file, labeling = True):
    processed = []

    with open(input_file, "r") as f:
        for line in f:
            entry = json.loads(line.strip())
            context = format_chat_as_story(reversed(entry["previous_messages"]))
            game_state = interpret_advantage(entry["time_str"], entry["radiant_gold_adv"], entry["radiant_xp_adv"])
            kills = format_kills(entry["killed_before_time"], passive=entry["hero_name"], active="killed")
            deaths = format_kills(entry["killed_by_before_time"], passive=entry["hero_name"], active="has been killed by")
            extra_info = f"{game_state}\n{kills} {deaths}"
            message = f"[MESSAGE TO CLASSIFY]!!!\n{format_message_as_statement(entry["hero_name"], entry["team"], entry["msg"])}\n"
            full_context = f"[GAME STATE]\n{extra_info}\n[CONTEXT]\n{context}\n"
            if labeling:
                label = 1 if entry["toxicity"].upper() == "TOXIC" else 0
                processed.append({
                    "message": message,
                    "context": full_context,
                    "label": label
                })
            else:
                processed.append({
                    "message": message,
                    "context": full_context
                })

    # Save to CSV
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["message", "context"]
        if labeling:
            fieldnames += ["label"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in processed:
            writer.writerow(row)

    print(f"Processed {len(processed)} entries and saved to {output_file}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preprocess dataset into split format.")
    parser.add_argument(
        "-i", "--input",
        type=str,
        default=DEFAULT_INPUT,
        help="Input JSONL file path (default: datasets/labeled_dataset.jsonl)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=DEFAULT_OUTPUT,
        help="Output CSV file path (default: datasets/processed_split.csv)"
    )
    args = parser.parse_args()
    print(args.input)
    print(args.output)

    process_jsonl_to_csv(args.input, args.output)