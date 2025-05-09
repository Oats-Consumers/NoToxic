import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from scripts.build_unlabeled_dataset import collect_contexts_from_match
from utils.game_info import load_hero_data, load_chatwheel_data, fetch_match_data
from inference.match_chat_labeler import label_match
app = Flask(__name__)
CORS(app)

def predict_toxicity(contexts):
    # Save messages to a JSON file
    with open("backend/contexts.json", "w") as json_file:
        json.dump(contexts, json_file, indent=4)
    label_match("backend/contexts.json", "backend/messages_output.json")
    
hero_names, npc_names, npc_to_id = load_hero_data("data/heroes.json")
chatwheel_data = load_chatwheel_data("data/chat_wheel.json")
@app.route('/get-toxic-messages', methods=['GET', 'POST'])
def get_toxic_messages():
    match_id = request.args.get('match_id')
    raw_match = fetch_match_data(match_id)
    players_data = raw_match.get("players", [])
    players_info = [
        {
            "player_slot": player.get("player_slot"),
            "player_name": player.get("personaname"),
            "hero_id": player.get("hero_id"),
            "hero_name": hero_names.get(player.get("hero_id"), "Unknown Hero")  # Lookup heroname

        }
        for player in players_data
    ]
    print(players_info)
    if not match_id:
        return jsonify({"error": "No match_id provided"}), 400
    contexts = collect_contexts_from_match(match_id, hero_names, npc_names, npc_to_id, chatwheel_data)
    predict_toxicity(contexts)
    messages_output_path = os.path.join(os.path.dirname(__file__), "messages_output.json")
    if not os.path.exists(messages_output_path):
        return jsonify({"error": "messages_output.json not found"}), 500

    with open(messages_output_path, "r", encoding="utf-8") as f:
        messages_output = [json.loads(line) for line in f]

    # Ensure the lengths of contexts and messages_output match
    if len(contexts) != len(messages_output):
        return jsonify({"error": "Mismatch between contexts and messages_output lengths"}), 500

    # Add labels to contexts
    for i in range(len(contexts)):
        contexts[i]["label"] = messages_output[i]["label"]
        for player in players_info:
            if player["hero_name"] in contexts[i]["hero_name"]:
                contexts[i]["player_name"] = player["player_name"]
                contexts[i]["hero_id"] = player["hero_id"]
                break
    open("backend/contexts.json", "w").close()
    open("backend/messages_output.json", "w").close()
    return jsonify(contexts)

if __name__ == '__main__':
    app.run(debug=True)