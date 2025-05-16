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

def label_match(input_path):
    print(f"Input path: {input_path}")
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_csv:
        temp_csv_path = temp_csv.name

    jsonl_to_model_input_converter.process_jsonl_to_csv(input_path, temp_csv_path, False)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"✅ Using GPU: {torch.cuda.get_device_name(0)}")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
        print("✅ Using MPS (Metal) on macOS")
    else:
        device = torch.device("cpu")
        print("⚠️ Using CPU")
    pipeline("text-classification", model=model, tokenizer=tokenizer, device=device)

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

    os.remove(temp_csv_path)
    return labeled_output
    
def predict_toxicity(contexts):
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_json:
        temp_json_path = temp_json.name
    with open(temp_json_path, "w") as json_file:
        json.dump(contexts, json_file, indent=4)
    print(f"Contexts saved to {temp_json_path}")
    labeled_output = label_match(temp_json_path)
    os.remove(temp_json_path)
    return labeled_output

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
