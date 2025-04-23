import json
from openai import OpenAI
from my_secrets import OPENAI_API_KEY

# Config
UNLABELED_PATH = "datasets/unlabeled_dataset.jsonl"
LABELED_PATH = "datasets/labeled_dataset.jsonl"
NUM_ENTRIES = 0     # Number of entries to label
START_INDEX = 978      # Change this to start from a different index
MODEL = "gpt-4o"

client = OpenAI(api_key=OPENAI_API_KEY)

def build_prompt(entry):
    previous = "\n  ".join(entry["previous_messages"]) or "None"
    kills = json.dumps(entry.get("killed_before_time", {}), ensure_ascii=False)
    deaths = json.dumps(entry.get("killed_by_before_time", {}), ensure_ascii=False)

    return f"""
You are a language model assisting in the classification of in-game Dota 2 chat messages based on their toxicity.

A message is considered:
- TOXIC if it includes insults, harassment, personal attacks, passive-aggressive behavior, excessive blame, flaming, or is clearly meant to provoke or demoralize teammates or opponents.
- NON-TOXIC if the message is neutral, strategic (e.g. map calls or team directions), cooperative, encouraging, humorous without hostility, or simply expressing emotion in a harmless way.

Use the full context provided — including game state, hero performance, and recent chat — to make a well-informed judgment.

The context below describes the state of the match **at the exact moment the message was sent**:

- Game Time (MM:SS): {entry['time_str']}
- Radiant Gold Advantage: {entry['radiant_gold_adv']} (positive = Radiant is ahead, negative = Dire is ahead)
- Radiant XP Advantage: {entry['radiant_xp_adv']} (positive = Radiant is ahead, negative = Dire is ahead)
- Heroes Killed by This Player Before This Message: {kills}
- Heroes That Killed This Player Before This Message: {deaths}
- Previous Messages From Players (most recent last):
  {previous}
- Team of the Player: {entry['team']}
- Player's Hero: {entry['hero_name']}
- Message To Be Assessed: "{entry['msg']}"

Your task: Based on all of the above, respond with a single word — either TOXIC or NON-TOXIC.
""".strip()

def label_entries(entries):
    labeled = []
    for i, entry in enumerate(entries):
        prompt = build_prompt(entry)

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            label = response.choices[0].message.content.strip().upper()
            entry["toxicity"] = label
            print(f"[{i+1}/{len(entries)}] {entry['msg']} → {label}")
            labeled.append(entry)
        except Exception as e:
            print(f"Error at entry {i + 1}: {e}")
    return labeled

def load_unlabeled_dataset(path, start_index, count):
    with open(path, "r", encoding="utf-8") as f:
        all_lines = f.readlines()
        selected_lines = all_lines[start_index-1:start_index-1 + count]
        return [json.loads(line) for line in selected_lines]

def append_labeled_dataset(path, entries):
    with open(path, "a", encoding="utf-8") as f:
        for entry in entries:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")

if __name__ == "__main__":
    unlabeled = load_unlabeled_dataset(UNLABELED_PATH, START_INDEX, NUM_ENTRIES)
    labeled = label_entries(unlabeled)
    append_labeled_dataset(LABELED_PATH, labeled)
    print(f"\n✅ Labeled {len(labeled)} entries starting from index {START_INDEX}. Appended to {LABELED_PATH}.")
