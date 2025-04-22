import json


UNLABELED_PATH = "datasets/unlabeled_dataset.jsonl"
LABELED_PATH = "datasets/labeled_dataset.jsonl"
START_INDEX = 1066      # Change this to start from a different index

def clean_non_toxic_entries(labeled_path, unlabeled_path, start_index=0):
    # Load labeled entries
    with open(labeled_path, "r", encoding="utf-8") as f:
        labeled_lines = f.readlines()

    with open(unlabeled_path, "r", encoding="utf-8") as f:
        unlabeled_lines = f.readlines()

    # Track which labeled entries to keep
    cleaned_labeled_lines = []
    cleaned_unlabeled_lines = []

    for i, labeled_line in enumerate(labeled_lines):
        if i < start_index:
            # Keep all lines before the starting index
            cleaned_labeled_lines.append(labeled_line)
            cleaned_unlabeled_lines.append(unlabeled_lines[i] if i < len(unlabeled_lines) else "")
            continue

        try:
            labeled_entry = json.loads(labeled_line)
            toxicity = labeled_entry.get("toxicity", "").upper()

            if toxicity == "TOXIC":
                cleaned_labeled_lines.append(labeled_line)
                if i < len(unlabeled_lines):
                    cleaned_unlabeled_lines.append(unlabeled_lines[i])
            else:
                print(f"🗑️ Removing NON-TOXIC entry at index {i}: {labeled_entry['msg']}")
        except Exception as e:
            print(f"⚠️ Error parsing line {i}: {e}")
            # Keep it just in case
            cleaned_labeled_lines.append(labeled_line)
            if i < len(unlabeled_lines):
                cleaned_unlabeled_lines.append(unlabeled_lines[i])

    # Overwrite labeled dataset
    with open(labeled_path, "w", encoding="utf-8") as f:
        f.writelines(cleaned_labeled_lines)

    # Overwrite unlabeled dataset
    with open(unlabeled_path, "w", encoding="utf-8") as f:
        f.writelines(cleaned_unlabeled_lines)

    print(f"\n✅ Cleanup complete. NON-TOXIC entries removed starting from index {start_index}.")

if __name__ == "__main__":
    clean_non_toxic_entries(LABELED_PATH, UNLABELED_PATH, START_INDEX)