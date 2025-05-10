import json
import csv

INPUT_PATH = "datasets/labeled_dataset.jsonl"
OUTPUT_PATH = INPUT_PATH.replace(".jsonl", ".csv")

def flatten_entry(entry):
    return {
        "time": entry["time"],
        "time_str": entry["time_str"],
        "hero_name": entry["hero_name"],
        "team": entry["team"],
        "msg": entry["msg"],
        "previous_messages": "\n".join(entry["previous_messages"]).replace("\n", "\\n"),
        "killed_before_time": json.dumps(entry["killed_before_time"], ensure_ascii=False),
        "killed_by_before_time": json.dumps(entry["killed_by_before_time"], ensure_ascii=False),
        "radiant_gold_adv": entry["radiant_gold_adv"],
        "radiant_xp_adv": entry["radiant_xp_adv"],
        "toxicity": entry["toxicity"]
    }

def convert_jsonl_to_csv(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as infile:
        entries = [json.loads(line) for line in infile]

    flattened = [flatten_entry(e) for e in entries]
    fieldnames = flattened[0].keys()

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_ALL,
            quotechar='"'
        )
        writer.writeheader()
        writer.writerows(flattened)

    print(f"✅ Converted {len(flattened)} entries to CSV at: {output_path}")

if __name__ == "__main__":
    convert_jsonl_to_csv(INPUT_PATH, OUTPUT_PATH)
