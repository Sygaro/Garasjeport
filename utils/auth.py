# utils/auth.py
import os
import json
from flask import request, jsonify
from functools import wraps

from config.config_paths import CONFIG_AUTH_PATH

CONFIG_AUTH_PATH = os.path.join("config", "config_auth.json")


def load_auth_config():
    try:
        with open(CONFIG_AUTH_PATH) as f:
            return json.load(f)
    except:
        return {}


def check_token():
    """
    Sjekker Authorization-header. Støtter:
    - Bare token
    - Bearer token
    """
    config = load_auth_config()
    header = request.headers.get("Authorization", "")
    token = header.replace("Bearer ", "").strip()
    allowed_tokens = [u.get("token") for u in config.get("users", {}).values()]
    return token in allowed_tokens



def check_webhook_key():
    """
    Tillater webhook-kall med /route?key=webhook-key
    """
    config = load_auth_config()
    key = request.args.get("key")
    return key in config.get("webhook_keys", [])

def load_token():
    try:
        with open(CONFIG_AUTH_PATH) as f:
            config = json.load(f)
        return config.get("token")
    except:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = load_token()
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401
        if auth_header.split(" ")[1] != token:
            return jsonify({"error": "Unauthorized"}), 403
        return f(*args, **kwargs)
    return decorated
