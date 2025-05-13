import json

def contains_word(word, text):
    return word.lower() in text.lower()

def check(file1, file2 = "datasets/random_100_label_dataset.jsonl"):
    tp = fp = tn = fn = 0
    unsure = 0
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        lines1 = [json.loads(line) for line in f1 if line.strip()]
        lines2 = [json.loads(line) for line in f2 if line.strip()]
    for i, (entry1, entry2) in enumerate(zip(lines1, lines2)):
        has_word_1 = entry1['toxicity'] == 'TOXIC'
        has_word_2 = entry2['toxicity'] == 'TOXIC'
        has_unsure = contains_word('UNSURE', entry1['toxicity'])
        if has_unsure:
            unsure += 1
            print("Unsure on index: ", i + 1)
            print("With text: ", json.dumps(entry1, indent=4))
            if has_word_2 == True:
                tp += 1
            else:
                tn += 1
            #input("Press any letter to go to the next iteration...")

        elif has_word_1 == has_word_2:
            if has_word_1 == True:
                tp += 1
            else:
                tn += 1
        else:
            if has_word_1 == True:
                print("False positive on index: ", i + 1)
                print("With text: ", json.dumps(entry1, indent=4))
                fn += 1
            else:
                print("False negative on index: ", i + 1)
                print("With text: ", json.dumps(entry1, indent=4))
                fp += 1
            input("Press any letter to go to the next iteration...")
    print("Unsure: ", unsure)
    print("True Positive: ", tp)
    print("False Positive: ", fp)
    print("True Negative: ", tn)
    print("False Negative: ", fn)
    print("f1 score: ", 2 * tp / (2 * tp + fp + fn))
    print("accuracy: ", (tp + tn) / (tp + tn + fp + fn))
    print("precision: ", tp / (tp + fp))
    print("recall: ", tp / (tp + fn))


if __name__ == "__main__":
    print("\n\n\n\n\n\n")
    check("datasets/random_100_label_check_0.jsonl")
    print("\n\n\n\n\n\n")
    # check("datasets/random_100_label_check_1.jsonl")
    # print("\n\n\n\n\n\n")
    # check("datasets/random_100_label_check_2.jsonl")
    # print("\n\n\n\n\n\n")
    # check("datasets/random_50_label_check_3.jsonl")
    # print("\n\n\n\n\n\n")
    # check("datasets/random_50_label_check_4.jsonl")
    # print("\n\n\n\n\n\n")
    # check("datasets/random_50_label_check_5.jsonl")