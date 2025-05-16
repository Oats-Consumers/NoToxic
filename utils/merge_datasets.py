import json


def load_jsonl(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]


def save_jsonl(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')


def merge_toxicity_labels(filepaths, procedure="precision"):
    # Load the three datasets
    datasets = [load_jsonl(path) for path in filepaths]

    # Ensure all datasets have the same number of entries
    length = len(datasets[0])
    if not all(len(ds) == length for ds in datasets):
        raise ValueError("Mismatch in number of entries between datasets.")

    merged_data = []
    for i in range(length):
        entries = [ds[i] for ds in datasets]
        labels = [entry['toxicity'] for entry in entries]

        toxic_count = labels.count('TOXIC')
        non_toxic_count = labels.count('NON-TOXIC')

        # Decide final label based on your logic
        final_label = ""

        if procedure == "precision":
            if toxic_count == 3:
                final_label = 'TOXIC'
            else:
                final_label = 'NON-TOXIC'

        if procedure == "voting":
            if toxic_count > non_toxic_count:
                final_label = 'TOXIC'
            else:
                final_label = 'NON-TOXIC'

        # Copy one of the entries and update its label
        merged_entry = dict(entries[0])
        merged_entry['toxicity'] = final_label
        merged_data.append(merged_entry)

    return merged_data


if __name__ == "__main__":
    input_paths = [
        'datasets/labeled_dataset_alain.jsonl',
        'datasets/labeled_dataset_imran.jsonl',
        'datasets/labeled_dataset_jose.jsonl',
    ]
    output_path_precision = 'datasets/labeled_dataset.jsonl'
    output_path_voting = 'datasets/labeled_dataset_voting.jsonl'

    merged = merge_toxicity_labels(input_paths)
    save_jsonl(merged, output_path_precision)

    print(f"Merged dataset written to {output_path_precision}")

    merged = merge_toxicity_labels(input_paths, procedure="voting")
    save_jsonl(merged, output_path_voting)

    print(f"Merged dataset (voting) written to {output_path_voting}")
