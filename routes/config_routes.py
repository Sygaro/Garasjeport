# ==========================================
# Filnavn: config_routes.py
# API-endepunkter for henting og lagring av config.json
# ==========================================

from flask import Blueprint, jsonify, request
import json
import os

config_routes = Blueprint("config_routes", __name__)

CONFIG_PATH = "config.json"

@config_routes.route("/api/config", methods=["GET"])
def get_config():
    """Returnerer hele config.json som JSON."""
    if not os.path.exists(CONFIG_PATH):
        return jsonify({"error": "Config ikke funnet"}), 404
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    return jsonify(config)

@config_routes.route("/api/config", methods=["PUT"])
def update_config():
    """Oppdaterer config.json basert på innsendt JSON-data."""
    try:
        new_config = request.get_json()

        with open(CONFIG_PATH, 'w') as f:
            json.dump(new_config, f, indent=2)

        return jsonify({"status": "OK", "message": "Konfigurasjon oppdatert"}), 200

    except Exception as e:
        return jsonify({"status": "Feil", "message": str(e)}), 400
