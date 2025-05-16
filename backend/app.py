import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, redirect, request, session, url_for, jsonify
from openid.consumer.consumer import Consumer, SUCCESS
from flask_cors import CORS
from backend.request_handler import request_label_chat, request_player_matches, request_win_lose_amount, request_reparse_match
import re

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
    
@app.route('/label-chat', methods=['GET'])
def label_chat():
    match_id = request.args.get('match_id')
    return request_label_chat(match_id)

@app.route('/player-matches')
def player_matches():
    account_id = request.args.get("account_id") or session.get("steam_id")
    offset = request.args.get('offset', default=0, type=int)
    return request_player_matches(account_id, offset)

@app.route('/win-lose-amount')
def win_lose_amount():
    account_id = request.args.get("account_id") or session.get("steam_id")
    return request_win_lose_amount(account_id)

@app.route('/reparse-match')
def reparse_match():
    match_id = request.args.get('match_id')
    return request_reparse_match(match_id)

if __name__ == "__main__":
    app.run(debug=True)
