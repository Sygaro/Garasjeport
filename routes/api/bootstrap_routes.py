from flask import Blueprint, jsonify
from config import config_paths
from utils.auth import token_required
from utils.logging.unified_logger import get_logger
import logging



import json, os
from datetime import datetime

bootstrap_routes = Blueprint("bootstrap_routes", __name__, url_prefix="/bootstrap")
logger = logging.getLogger("bootstrap_routes")

# logger = get_logger("bootstrap_routes" category="system", source="API")


@bootstrap_routes.route("/status", methods=["GET"])
@token_required
def get_bootstrap_status():
    logger.debug("Kall mottatt: /bootstrap/status")
    
    path = config_paths.STATUS_BOOTSTRAP_PATH

    if not path.exists():
        logger.warning(f"Statusfil ikke funnet: {path}")
        return jsonify({
            "status": "unknown",
            "timestamp": None,
            "details": "Statusfil ikke funnet"
        }), 404

    try:
        with open(path, "r") as f:
            data = json.load(f)
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Feil ved lesing av statusfil: {e}")
        return jsonify({
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "details": f"Feil ved lesing av statusfil: {str(e)}"
        }), 500


@bootstrap_routes.route("/ping", methods=["GET"])
@token_required
def bootstrap_ping():
    logger.debug("Kall mottatt: /bootstrap/ping")
    path = config_paths.STATUS_BOOTSTRAP_PATH

    if not path.exists():
        return jsonify({"ping": "not_ready"}), 503

    try:
        with open(path, "r") as f:
            data = json.load(f)
            status = data.get("status", "").lower()
            if status == "ok":
                return jsonify({"ping": "ok"}), 200
            else:
                return jsonify({"ping": status}), 503
    except Exception as e:
        logger.error(f"Feil ved ping-lesing: {e}")
        return jsonify({"ping": "error", "details": str(e)}), 500
