import argparse
import json
import sys
import tempfile
import os
import csv
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline

from utils import jsonl_to_model_input_converter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_INPUT = os.path.join(SCRIPT_DIR, "..", "matches", "saved_match.jsonl")
DEFAULT_OUTPUT = os.path.join(SCRIPT_DIR, "..", "matches", "saved_match_output.jsonl")
MODEL_PATH = os.path.join(SCRIPT_DIR, "..", "training", "models", "best-s-nlp-roberta-toxicity-classifier-split")

def label_match(input_path, output_path):
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_csv:
        temp_csv_path = temp_csv.name

    jsonl_to_model_input_converter.process_jsonl_to_csv(input_path, temp_csv_path, False)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    tokenizer.additional_special_tokens({"spec"})
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, device=device)

    labeled_output = []
    with open(temp_csv_path, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            context = row["context"]
            message = row["message"]

            inputs = tokenizer(
                message,
                context,
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors="pt"
            ).to(device)

            # Decode input_ids back to tokens
            # print("\n--- TOKENIZED MESSAGE+CONTEXT INPUT ---")
            # print("Tokens:", tokenizer.convert_ids_to_tokens(inputs['input_ids'][0]))
            # print("Decoded text:", tokenizer.decode(inputs['input_ids'][0], skip_special_tokens=True))
            # print("Attention mask:", inputs['attention_mask'][0])
            # print("Input length:", inputs['input_ids'].shape[1])

            with torch.no_grad():
                outputs = model(**inputs)
                scores = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
                label_id = torch.argmax(scores).item()
                label = model.config.id2label[label_id]
                confidence = scores[label_id].item()

            labeled_output.append({
                "message": message,
                "context": context,
                "label": label,
                "confidence": confidence
            })

    with open(output_path, "w", encoding="utf-8") as out_file:
        for item in labeled_output:
            out_file.write(json.dumps(item) + "\n")

    # Clean up temp file
    os.remove(temp_csv_path)
    print(f"Labeled output written to {output_path}")


if __name__ == "__main__":
    curr = sys.path.append("..")

    parser = argparse.ArgumentParser(description="Labels the chats of a match")
    parser.add_argument(
        "-i", "--input",
        type=str,
        default=DEFAULT_INPUT,
        help="Input JSONL file path (default: matches/saved_match.jsonl)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=DEFAULT_OUTPUT,
        help="Output JSONL file path (default: matches/saved_match_output.jsonl)"
    )
    args = parser.parse_args()
    label_match(args.input, args.output)
