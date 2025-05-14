import json

input_file = "datasets/random_100_dataset.jsonl"
output_file = "datasets/random_100_label_dataset.jsonl"

with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        data = json.loads(line)
        data["toxicity"] = "TOXIC"
        outfile.write(json.dumps(data) + "\n")
