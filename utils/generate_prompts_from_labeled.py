import json

LABELED_PATH = "datasets/labeled_dataset.jsonl"

# Example sets — replace/update as needed
FALSE_NEGATIVES = [784, 945, 396, 265]
FALSE_POSITIVES = [537, 219]
TRUE_NEGATIVES  = [52, 549]
TRUE_POSITIVES  = [743, 561]

def load_entries_by_line_indices(path, indices):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        return [json.loads(lines[i - 1]) for i in indices]

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

def print_prompts(label, indices):
    entries = load_entries_by_line_indices(LABELED_PATH, indices)
    for idx, entry in zip(indices, entries):
        print("=" * 80)
        print(f"📌 Entry #{idx} — {label}")
        print("=" * 80)
        print(build_prompt(entry))
        print()

if __name__ == "__main__":
    print_prompts("False Negative", FALSE_NEGATIVES)
    print_prompts("False Positive", FALSE_POSITIVES)
    print_prompts("True Negative", TRUE_NEGATIVES)
    print_prompts("True Positive", TRUE_POSITIVES)
