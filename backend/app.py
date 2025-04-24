from flask import Flask, request, jsonify
import requests
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os
from flask_cors import CORS
from match_chat_labeler import label_match

app = Flask(__name__)
CORS(app)
MODEL_DIR = "../training/models/best-s-nlp-roberta-toxicity-classifier-split"

if not os.path.exists(MODEL_DIR):
    raise FileNotFoundError(f"Model directory not found: {MODEL_DIR}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR, local_files_only=True)
model.eval()

def predict_toxicity(messages):
    inputs = tokenizer(messages, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        preds = torch.argmax(probs, dim=1)
    return preds.tolist()

@app.route('/get-toxic-messages', methods=['GET', 'POST'])
@app.route('/get-toxic-messages', methods=['GET'])
def get_toxic_messages():
    match_id = request.args.get('match_id')

    if not match_id:
        return jsonify({"error": "No match_id provided"}), 400

    # Fetch match data from OpenDota
    response = requests.get(f"https://api.opendota.com/api/matches/{match_id}")
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch match data"}), 500

    match_data = response.json()
    chat = match_data.get("chat", [])

    if not chat:
        return jsonify({"message": "No chat messages found"}), 200

    # Sort chat messages by time
    chat_sorted = sorted(
        [msg for msg in chat if "key" in msg and isinstance(msg["key"], str)],
        key=lambda x: x.get("time", 0)
    )

    messages = [msg["key"] for msg in chat_sorted]
    toxic_flags = predict_toxicity(messages)

    # Package enriched message data
    enriched_messages = [
        {
            "player_slot": msg.get("player_slot", "Unknown"),
            "time": msg.get("time", 0),
            "text": msg["key"],
            "toxic": bool(is_toxic)
        }
        for msg, is_toxic in zip(chat_sorted, toxic_flags)
    ]

    return jsonify({"messages": enriched_messages})


if __name__ == '__main__':
    app.run(debug=True)


from flask import Flask, jsonify, request
