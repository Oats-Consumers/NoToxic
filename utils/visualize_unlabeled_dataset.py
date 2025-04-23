import json

def pretty_print_entry(entry):
    print("\n--- Chat Message Context ---")
    print(f"🕒 Time: {entry['time_str']}")
    print(f"📈 Radiant Gold Adv: {entry['radiant_gold_adv']}")
    print(f"📚 Radiant XP Adv: {entry['radiant_xp_adv']}")
    
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

def load_dataset(file_path="datasets/unlabeled_dataset.jsonl"):
    with open(file_path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

if __name__ == "__main__":
    dataset = load_dataset()

    for i, entry in enumerate(dataset):
        print(f"\n📝 Entry #{i+1}")
        pretty_print_entry(entry)

        user_input = input("Press Enter to continue, or type 'q' to quit: ").strip().lower()
        if user_input == 'q':
            break
