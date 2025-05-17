# ==========================================
# Filnavn: config_routes.py
# API-endepunkter for å lese/endre config.json
# ==========================================

from flask import Blueprint, jsonify, request
from controllers.config import load_config, save_config

config_routes = Blueprint("config_routes", __name__)

@config_routes.route("/api/config", methods=["GET"])
def get_config():
    """
    Returnerer hele konfigurasjonen (config.json)
    """
    config_data = load_config()
    return jsonify(config_data), 200

@config_routes.route("/api/config", methods=["PUT"])
def update_config():
    """
    Oppdaterer hele config.json basert på innsendt JSON.
    """
    new_config = request.get_json(force=True, silent=True)
    if not new_config:
        return jsonify({"error": "Ugyldig eller manglende JSON"}), 400

    try:
        save_config(new_config)
        return jsonify({"message": "Konfigurasjon oppdatert"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
