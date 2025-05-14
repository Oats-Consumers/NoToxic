import json
import random

OUTPUT_FILE = "datasets/random_100_dataset.jsonl"
INPUT_FILE = "datasets/unlabeled_dataset.jsonl"
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = [json.loads(line) for line in f]
sampled_data = random.sample(data, 100)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for item in sampled_data:
        f.write(json.dumps(item) + "\n")
