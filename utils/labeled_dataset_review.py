import json
import random
from collections import Counter

LABELED_PATH = "datasets/random_100_label_dataset.jsonl"

def pretty_print_entry(entry, index=None):
    print("\n=== 🧠 Labeled Chat Message Context ===")
    if index is not None:
        print(f"📄 Entry #{index + 1}")
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

    killed = entry["killed_before_time"]
    killed_by = entry["killed_by_before_time"]

    print(f"💀 Killed (before msg): {killed if killed else '{}'}")
    print(f"☠️  Killed By (before msg): {killed_by if killed_by else '{}'}")
    print(f"💬 Message: {entry['msg']}")
    print(f"⚠️ Current Label: {'🔥 TOXIC' if entry['toxicity'] == 'TOXIC' else '✅ NON-TOXIC'}")

def load_dataset(path=LABELED_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def save_dataset(dataset, path=LABELED_PATH):
    with open(path, "w", encoding="utf-8") as f:
        for entry in dataset:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")

def review_entries(dataset):
    indices = list(range(len(dataset)))
    random.shuffle(indices)
    changes = 0

    for i in range(0, dataset.__len__(), 1):
        entry = dataset[i]
        pretty_print_entry(entry, index=i)

        user_input = input("Enter new label (t/n), Enter to skip, or 'q' to quit: ").strip().lower()

        if user_input == 'q':
            break
        elif user_input == 't':
            if entry["toxicity"] != "TOXIC":
                entry["toxicity"] = "TOXIC"
                changes += 1
        elif user_input == 'n':
            if entry["toxicity"] != "NON-TOXIC":
                entry["toxicity"] = "NON-TOXIC"
                changes += 1
        else:
            continue

    print(f"\n💾 Modified {changes} entries.")
    return dataset

if __name__ == "__main__":
    dataset = load_dataset()

    # Show stats before review
    counts = Counter(entry["toxicity"] for entry in dataset)
    print("=== 🧮 Dataset Summary ===")
    print(f"Total Messages: {len(dataset)}")
    print(f"🔥 TOXIC: {counts.get('TOXIC', 0)}")
    print(f"✅ NON-TOXIC: {counts.get('NON-TOXIC', 0)}")

    updated_dataset = review_entries(dataset)
    save_dataset(updated_dataset)

    print("✅ Dataset updated and saved.")
