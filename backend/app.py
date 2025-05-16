import sys
import os
import re
from flask import Flask, redirect, request, session, url_for, jsonify
from openid.consumer.consumer import Consumer, SUCCESS
from flask_cors import CORS

# Set up path and secrets
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from my_secrets import FLASK_SECRET_KEY, FRONTEND_ORIGIN
from backend.request_handler import (
    request_label_chat,
    request_player_matches,
    request_win_lose_amount,
    request_reparse_match
)

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY


# CORS config (adjust as needed for prod)
CORS(
    app,
    origins=[FRONTEND_ORIGIN]
)

# Routes

@app.route("/label-chat", methods=["GET"])
def label_chat():
    match_id = request.args.get('match_id')
    try:
        return request_label_chat(match_id)
    except Exception as e:
        app.logger.error(f"Error labeling chat for match {match_id}: {e}")
        return jsonify({"error": "Failed to label chat"}), 500

@app.route("/player-matches")
def player_matches():
    account_id = request.args.get("account_id") or session.get("steam_id")
    offset = request.args.get('offset', default=0, type=int)
    try:
        return request_player_matches(account_id, offset)
    except Exception as e:
        app.logger.error(f"Error fetching player matches: {e}")
        return jsonify({"error": "Failed to fetch matches"}), 500

@app.route("/win-lose-amount")
def win_lose_amount():
    account_id = request.args.get("account_id") or session.get("steam_id")
    try:
        return request_win_lose_amount(account_id)
    except Exception as e:
        app.logger.error(f"Error fetching win/lose stats: {e}")
        return jsonify({"error": "Failed to fetch win/lose amount"}), 500

@app.route("/reparse-match")
def reparse_match():
    match_id = request.args.get('match_id')
    try:
        return request_reparse_match(match_id)
    except Exception as e:
        app.logger.error(f"Error reparsing match {match_id}: {e}")
        return jsonify({"error": "Failed to reparse match"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
