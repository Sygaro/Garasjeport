from utils.logging.unified_logger import get_logger
from flask import Blueprint, jsonify, request
from core.config_manager import ConfigManager
from utils.auth import token_required


config_routes = Blueprint("config_routes", __name__)
manager = ConfigManager()

@config_routes.route("/api/config/<module>", methods=["GET"])
@token_required
def get_config_module(module):

    """
    Returnerer en spesifikk konfigmodul (gpio, system, logging)
    """
    try:
        config = manager.get_module(module)
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": f"Feil ved henting av modul '{module}': {str(e)}"}), 500

@config_routes.route("/api/config/<module>", methods=["PUT"])
@token_required
def update_config_module(module):
    """
    Oppdaterer en spesifikk konfigmodul
    """
    try:
        data = request.get_json()
        manager.update_module(module, data, user="admin", source="web")
        return jsonify({"status": "OK", "message": f"Modul '{module}' lagret"})
    except Exception as e:
        return jsonify({"error": f"Feil ved lagring av modul '{module}': {str(e)}"}), 500
