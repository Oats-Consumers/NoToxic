from scripts.build_unlabeled_dataset import collect_contexts_from_match
from utils.game_info import load_hero_data, load_chatwheel_data, fetch_match_data
from inference.match_chat_labeler import predict_toxicity
from clients import OPEN_DOTA_CLIENT
import time
from flask import jsonify

hero_names, npc_names, npc_to_id = load_hero_data("data/heroes.json")
chatwheel_data = load_chatwheel_data("data/chat_wheel.json")

def request_label_chat(match_id):
    if not match_id:
        return jsonify({"error": "No match_id provided"}), 400
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
    contexts = collect_contexts_from_match(match_id, hero_names, npc_names, npc_to_id, chatwheel_data)
    print("before predict_toxicity, contexts: ", contexts)
    labeled_output = predict_toxicity(contexts)
    print(f"labeled_output: {labeled_output}")
    if not labeled_output:
        return jsonify({"error": "No labeled output found"}), 50
    
    # Add labels to contexts
    for i in range(len(contexts)):
        contexts[i]["label"] = labeled_output[i]["label"]
        for player in players_info:
            if player["hero_name"] in contexts[i]["hero_name"]:
                contexts[i]["player_name"] = player["player_name"]
                contexts[i]["hero_id"] = player["hero_id"]
                break
    return jsonify(contexts)

def request_player_matches(account_id, offset):
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

def request_win_lose_amount(account_id):
    if not account_id:
        return jsonify({"error": "No account_id provided and not logged in"}), 401
    account_id = int(account_id)
    win_lose = OPEN_DOTA_CLIENT.get_player_win_lose(account_id)

    if not win_lose:
        return jsonify({"error": "No win/loss data found"}), 400
    return jsonify(win_lose)

def request_reparse_match(match_id, timeout=6000):
    if not match_id:
        return jsonify({"error": "No match_id provided"}), 400
    try:
        response = OPEN_DOTA_CLIENT.reparse_match(match_id)
        works = False
        if response.status_code != 200:
            return jsonify({"error": "This match has not yet been parsed, the reparse request failed!"}), response.status_code
        for retry in range(4):
            time.sleep(timeout//400)
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