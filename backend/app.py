import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, redirect, request, session, url_for, jsonify
from openid.consumer.consumer import Consumer, SUCCESS
import json
from flask_cors import CORS
from scripts.build_unlabeled_dataset import collect_contexts_from_match
from utils.game_info import load_hero_data, load_chatwheel_data, fetch_match_data
from inference.match_chat_labeler import label_match
import re
from clients import OPEN_DOTA_CLIENT
app = Flask(__name__)
app.secret_key = "supersecret"

store = None
temp_openid_session = {}  # ❗ Used instead of Flask session
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # or "None" if you're using HTTPS
app.config["SESSION_COOKIE_SECURE"] = False    # True only if served over HTTPS

CORS(app, supports_credentials=True, origins=["http://127.0.0.1:3000"])

@app.route("/")
def index():
    if "steam_id" in session:
        return f"✅ Logged in as: {session['steam_id']}"
    return '<a href="/login">Login with Steam</a>'

@app.route("/login")
def login():
    consumer = Consumer(temp_openid_session, store)
    auth_request = consumer.begin("https://steamcommunity.com/openid")
    return redirect(auth_request.redirectURL(
        realm=request.url_root,
        return_to=url_for("authorize", _external=True)
    ))

@app.route("/authorize")
def authorize():
    consumer = Consumer(temp_openid_session, store)
    response = consumer.complete(dict(request.args), request.url)

    if response.status == SUCCESS:
        steam_id = re.search(r"\d+$", response.getDisplayIdentifier()).group()
        session["steam_id"] = steam_id
        return redirect("http://127.0.0.1:3000")

    else:
        return "❌ Login failed."

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/check-login")
def check_login():
    steam_id = session.get("steam_id")
    if steam_id:
        return jsonify({"loggedIn": True, "steam_id": steam_id})
    return jsonify({"loggedIn": False}), 401

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
    raw_match = OPEN_DOTA_CLIENT.get_match_details(match_id)
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

@app.route('/player-recentmatches')
def get_toxic_messages_player():
    account_id = request.args.get("account_id") or session.get("steam_id")
    offset = request.args.get('offset', default=0, type=int)

    if not account_id:
        return jsonify({"error": "No account_id provided and not logged in"}), 401
    account_id = int(account_id)
    matches_id = OPEN_DOTA_CLIENT.get_player_matches(account_id, limit=20, offset=offset)
    player_info = OPEN_DOTA_CLIENT.get_player_info(account_id)

    if not matches_id:
        return jsonify({"error": "No match_id found for player"}), 400

    return jsonify({
        "player": player_info,
        "matches": matches_id
    })

@app.route('/win-lose-amount')
def get_win_lose_amount():
    account_id = request.args.get("account_id") or session.get("steam_id")
    if not account_id:
        return jsonify({"error": "No account_id provided and not logged in"}), 401
    account_id = int(account_id)
    win_lose = OPEN_DOTA_CLIENT.get_player_win_lose(account_id)

    if not win_lose:
        return jsonify({"error": "No win/loss data found"}), 400

    return jsonify(win_lose)

@app.route('/reparse-match')
def reparse_match():
    match_id = request.args.get('match_id')
    if not match_id:
        return jsonify({"error": "No match_id provided"}), 400

    try:
        response = OPEN_DOTA_CLIENT.reparse_match(match_id)
        works = False
        if response.status_code != 200:
            return jsonify({"error": "This match has not yet been parsed, the reparse request failed!"}), response.status_code
        for retry in range(4):
            time.sleep(15)
            match_data = fetch_match_data(match_id)
            chat_log = match_data.get("chat") if match_data else []
            if chat_log:
                works = True
                break
        else:
            print(f"❌ Couldn't parse the match, timeout")
            return jsonify({"error": "Couldn't parse the match, not all required data for this match may be available"}), 500
        if works:
            return jsonify({"message": "Match reparsed successfully"})
        else:
            return jsonify({"error": "This match has not yet been parsed, the reparse request failed!"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
