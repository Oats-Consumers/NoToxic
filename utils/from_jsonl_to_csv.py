import json
import csv


def jsonl_to_csv(jsonl_file, csv_file):
    with open(jsonl_file, 'r', encoding='utf-8') as infile, \
            open(csv_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["input_text", "label"])
        writer.writeheader()

        for line in infile:
            data = json.loads(line.strip())
            writer.writerow({
                "input_text": data["input_text"],
                "label": data["label"]
            })

    print(f"Converted {jsonl_file} to {csv_file}")


# Example usage:
jsonl_to_csv("/Users/joses/Documentos/Spring 2025/NoToxic/datasets/processed_toxicity_data.jsonl", "/Users/joses/Documentos/Spring 2025/NoToxic/datasets/processed_toxicity_data.csv")
