from utils.logging.unified_logger import get_logger
# routes/log_routes.py

from flask import Blueprint, jsonify, request
from utils.auth import token_required
from config import config_paths as paths
from utils.logging.logger_manager import get_logger
import os
import time

routes_logger = get_logger("routes", category="system")

log_routes = Blueprint("log_routes", __name__)

# Gyldige loggtyper og deres filbaner
VALID_LOGS = {
    "status": paths.LOG_STATUS_PATH,
    "error": paths.LOG_ERROR_PATH,
    "activity": paths.LOG_ACTIVITY_PATH,
    "timing": paths.LOG_TIMING_PATH,
    "bootstrap": paths.LOG_BOOTSTRAP_PATH
}

@log_routes.route("/log", methods=["GET"])
@token_required
def api_get_log():
    """
    Returnerer de siste linjene fra aktivitetsloggen.
    Valgfri query-param: ?lines=50 (default: 50)
    """
    try:
        lines_requested = int(request.args.get("lines", 50))
        if lines_requested <= 0:
            lines_requested = 50
    except (ValueError, TypeError):
        lines_requested = 50

    logs = routes_logger.get_recent_logs(limit=lines_requested)
    return jsonify({
        "logs": logs,
        "returned_lines": len(logs),
        "requested_lines": lines_requested
    })


@log_routes.route("/api/logs", methods=["GET"])
@token_required
def list_log_files():
    """
    Returnerer alle tilgjengelige loggtyper som API-et støtter.
    """
    return jsonify({
        "available_logs": list(VALID_LOGS.keys())
    })


@log_routes.route("/api/logs/<logtype>", methods=["GET"])
@token_required
def get_log(logtype):
    """
    Returnerer siste X linjer fra ønsket loggtype.
    Bruk valgfri query-param ?lines=50
    """
    log_path = VALID_LOGS.get(logtype.lower())
    if not log_path:
        return jsonify({"error": "Ugyldig loggtype"}), 400

    # Hent antall linjer fra query param
    try:
        lines_requested = int(request.args.get("lines", 50))
        if lines_requested <= 0:
            lines_requested = 50
    except (ValueError, TypeError):
        lines_requested = 50

    try:
        with open(log_path, "r") as f:
            all_lines = f.readlines()
            lines = all_lines[-lines_requested:]

        last_modified = time.ctime(os.path.getmtime(log_path))

        return jsonify({
            "logtype": logtype,
            "lines": lines,
            "total_lines": len(all_lines),
            "returned_lines": len(lines),
            "last_modified": last_modified
        })

    except FileNotFoundError:
        routes_logger.warning("API/get_log 404: Loggfil ikke funnet")
        return jsonify({"error": "Loggfil ikke funnet"}), 404
    