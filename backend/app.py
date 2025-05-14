import os
import sys
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Set up project root for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.build_unlabeled_dataset import collect_contexts_from_match
from utils.game_info import load_hero_data, load_chatwheel_data, fetch_match_data, fetch_recent_matches, fetch_player
from inference.match_chat_labeler import label_match

app = Flask(__name__)
CORS(app)  # You can restrict this with origins=["https://your.github.io/site"] in production
logging.basicConfig(level=logging.INFO)

# Load hero and chatwheel data
hero_names, npc_names, npc_to_id = load_hero_data("data/heroes.json")
chatwheel_data = load_chatwheel_data("data/chat_wheel.json")


def predict_toxicity(contexts):
    with open("backend/contexts.json", "w", encoding="utf-8") as json_file:
        json.dump(contexts, json_file, indent=4, ensure_ascii=False)
    label_match("backend/contexts.json", "backend/messages_output.json")

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "message": "Toxicity Ward backend is alive"}), 200

@app.route("/get-toxic-messages", methods=["GET", "POST"])
def get_toxic_messages():
    match_id = request.args.get("match_id")
    if not match_id:
        return jsonify({"error": "No match_id provided"}), 400

    try:
        raw_match = fetch_match_data(match_id)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch match: {str(e)}"}), 500

    players_data = raw_match.get("players", [])
    players_info = [
        {
            "player_slot": player.get("player_slot"),
            "player_name": player.get("personaname"),
            "hero_id": player.get("hero_id"),
            "hero_name": hero_names.get(player.get("hero_id"), "Unknown Hero"),
        }
        for player in players_data
    ]

    app.logger.info(f"Fetched players: {players_info}")

    try:
        contexts = collect_contexts_from_match(
            match_id, hero_names, npc_names, npc_to_id, chatwheel_data
        )
        predict_toxicity(contexts)
    except Exception as e:
        return jsonify({"error": f"Error during toxicity prediction: {str(e)}"}), 500

    messages_output_path = os.path.join(os.path.dirname(__file__), "messages_output.json")
    if not os.path.exists(messages_output_path):
        return jsonify({"error": "messages_output.json not found"}), 500

    with open(messages_output_path, "r", encoding="utf-8") as f:
        messages_output = [json.loads(line) for line in f]

    if len(contexts) != len(messages_output):
        return jsonify({"error": "Mismatch between contexts and messages_output lengths"}), 500

    # Add labels to contexts
    for i in range(len(contexts)):
        contexts[i]["label"] = messages_output[i]["label"]
        for player in players_info:
            if player["hero_name"] == contexts[i]["hero_name"]:
                contexts[i]["player_name"] = player["player_name"]
                contexts[i]["hero_id"] = player["hero_id"]
                break

    # Cleanup
    try:
        os.remove("backend/contexts.json")
        os.remove("backend/messages_output.json")
    except Exception as e:
        app.logger.warning(f"Failed to remove temp files: {e}")

    return jsonify(contexts)


def get_steam32(steam64_id):
    return str(int(steam64_id) - 76561197960265728)


@app.route("/player-recentmatches", methods=["GET"])
def get_toxic_messages_player():
    account_id_raw = request.args.get("account_id")
    if not account_id_raw:
        return jsonify({"error": "No account_id provided"}), 400

    account_id = get_steam32(account_id_raw)

    try:
        matches_id = fetch_recent_matches(account_id)
        player_info = fetch_player(account_id)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch player data: {str(e)}"}), 500

    return jsonify({
        "player": player_info,
        "matches": matches_id
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
