import json
from collections import Counter

def pretty_print_entry(entry):
    print("\n=== 🧠 Labeled Chat Message Context ===")
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
    print(f"⚠️ Toxicity Label: {'🔥 TOXIC' if entry['toxicity'] == 'TOXIC' else '✅ NON-TOXIC'}")

def load_dataset(file_path="datasets/random_50_label_check_2.jsonl"):
    with open(file_path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

if __name__ == "__main__":
    dataset = load_dataset()
    
    # 🔢 Count TOXIC / NON-TOXIC
    counts = Counter(entry["toxicity"] for entry in dataset)
    total = sum(counts.values())
    print("=== 🧮 Dataset Summary ===")
    print(f"Total Messages: {total}")
    print(f"🔥 TOXIC: {counts.get('TOXIC', 0)}")
    print(f"✅ NON-TOXIC: {counts.get('NON-TOXIC', 0)}")

    # 📝 Walk through entries
    for i, entry in enumerate(dataset):
        print(f"\n📄 Entry #{i+1}")
        pretty_print_entry(entry)

        user_input = input("Press Enter to continue, or type 'q' to quit: ").strip().lower()
        if user_input == 'q':
            break
