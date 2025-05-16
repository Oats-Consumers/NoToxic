import json
from collections import Counter
import os

LABELED_PATH = "datasets/labeled_dataset.jsonl"

def pretty_print_entry(entry, index=None, total=None):
    print("\n=== 🧠 Labeled Chat Message Context ===")
    if index is not None and total is not None:
        print(f"📄 Entry {index + 1}/{total}")
    print(f"🕒 Time: {entry['time_str']}")
    print(f"📈 Radiant Gold Advantage: {entry['radiant_gold_adv']}")
    print(f"📚 Radiant XP Advantage: {entry['radiant_xp_adv']}")
    print("🧾 Previous messages:")
    if entry["previous_messages"]:
        for line in entry["previous_messages"]:
            print(f"  → {line}")
    else:
        print("  None")
    print(f"👥 Team: {entry['team']}")
    print(f"🧝 Hero: {entry['hero_name']}")
    print(f"💬 Message: {entry['msg']}")
    print(f"💀 Killed (before msg): {entry['killed_before_time'] or '{}'}")
    print(f"☠️  Killed By (before msg): {entry['killed_by_before_time'] or '{}'}")
    print(f"⚠️ Current Label: {'🟨 UNSURE' if entry['toxicity'] == 'UNSURE' else entry['toxicity']}")

def load_dataset(path=LABELED_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def save_dataset(dataset, path=LABELED_PATH):
    with open(path, "w", encoding="utf-8") as f:
        for entry in dataset:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")

def review_unsure_entries(dataset):
    unsure_indices = [i for i, entry in enumerate(dataset) if entry.get("toxicity", "").upper() == "UNSURE"]
    total_unsure = len(unsure_indices)
    changes = 0

    if total_unsure == 0:
        print("✅ No entries labeled as UNSURE.")
        return dataset

    for idx, i in enumerate(unsure_indices):
        entry = dataset[i]
        pretty_print_entry(entry, index=idx, total=total_unsure)

        user_input = input("Change label? [t = TOXIC, n = NON-TOXIC, Enter = skip, q = quit]: ").strip().lower()

        if user_input == 'q':
            break
        elif user_input == 't':
            dataset[i]["toxicity"] = "TOXIC"
            changes += 1
        elif user_input == 'n':
            dataset[i]["toxicity"] = "NON-TOXIC"
            changes += 1
        # else do nothing (skip)

    print(f"\n🔁 Reviewed {len(unsure_indices)} UNSURE entries.")
    print(f"💾 Modified {changes} entries.")
    return dataset

if __name__ == "__main__":
    dataset = load_dataset()

    counts = Counter(entry["toxicity"] for entry in dataset)
    print("=== 🧮 Dataset Summary ===")
    print(f"Total Messages: {len(dataset)}")
    print(f"🔥 TOXIC: {counts.get('TOXIC', 0)}")
    print(f"✅ NON-TOXIC: {counts.get('NON-TOXIC', 0)}")
    print(f"🟨 UNSURE: {counts.get('UNSURE', 0)}")

    updated_dataset = review_unsure_entries(dataset)
    save_dataset(updated_dataset)
    print("✅ Dataset updated and saved.")
