import sys
import os
import re
from flask import Flask, redirect, request, session, url_for, jsonify
from openid.consumer.consumer import Consumer, SUCCESS
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

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

# ✅ Fix reverse proxy detection
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Flask session cookie settings
app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True,
    PREFERRED_URL_SCHEME="https"
)

# CORS config (adjust as needed for prod)
CORS(app, supports_credentials=True, origins=[
    "https://oats-consumers.github.io",
    "https://oats-consumers.github.io/NoToxic",  # optional
    "http://127.0.0.1:3000",
    "http://localhost:3000"
])

# Routes

@app.route("/")
def index():
    if "steam_id" in session:
        return f"✅ Logged in as: {session['steam_id']}"
    return '<a href="/login">Login with Steam</a>'

@app.route("/login")
def login():
    # 🔄 Use fresh memory-backed OpenID store
    consumer = Consumer({}, None)
    auth_request = consumer.begin("https://steamcommunity.com/openid")

    PUBLIC_BASE_URL = "https://30dlqduz990x74-5000.proxy.runpod.net"

    return redirect(auth_request.redirectURL(
        realm=PUBLIC_BASE_URL,
        return_to=f"{PUBLIC_BASE_URL}/authorize"
    ))

@app.route("/authorize")
def authorize():
    consumer = Consumer({}, None)
    response = consumer.complete(dict(request.args), request.url)

    print("🔥 Reached /authorize")
    print("📥 request.url:", request.url)
    print("📥 openid.return_to:", request.args.get("openid.return_to"))
    print("📥 response.status:", response.status)

    if response.status == SUCCESS:
        identifier = response.getDisplayIdentifier()
        print("✅ Identifier:", identifier)
        match = re.search(r"\d+$", identifier)
        if match:
            steam_id = match.group()
            session["steam_id"] = steam_id
            print("✅ Login success — steam_id:", steam_id)
            return redirect(FRONTEND_ORIGIN)
        print("❌ Could not extract Steam ID from identifier:", identifier)
        return "❌ Failed to extract Steam ID.", 400

    print("❌ OpenID login failed.")
    return "❌ Login failed.", 401

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
    app.run(host="0.0.0.0", port=5000, debug=False)
