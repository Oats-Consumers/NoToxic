import json


from clients import OPEN_AI_CLIENT

# Config
UNLABELED_PATH = "datasets/unlabeled_dataset.jsonl"
LABELED_PATH = "datasets/labeled_dataset.jsonl"
NUM_ENTRIES = 20     # Number of entries to label
START_INDEX = 1060      # Change this to start from a different index

def label_entries(entries):
    labeled = []
    for i, entry in enumerate(entries):
        try:
            label = OPEN_AI_CLIENT.label_entry(entry)
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
