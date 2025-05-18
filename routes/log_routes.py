# routes/log_routes.py

from flask import Blueprint, jsonify
import os

log_routes = Blueprint("log_routes", __name__)

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')

@log_routes.route("/api/logs/<logtype>")
def get_log(logtype):
    filename = f"{logtype}.log"
    log_path = os.path.join(LOG_DIR, filename)

    if not os.path.isfile(log_path):
        return jsonify({"error": "Logg ikke funnet"}), 404

    with open(log_path, 'r') as f:
        lines = f.readlines()[-200:] # ← endrer antall linjer som vises i web

    return jsonify({"lines": lines})
