from utils.logging.unified_logger import get_logger
# routes/api/timing_routes.py

from flask import Blueprint, jsonify
from utils.auth import token_required
from core.system import controller
from utils.config_loader import load_config
from config import config_paths as paths


timing_routes = Blueprint("timing_routes", __name__)

@timing_routes.route("/timing/<port>", methods=["GET"])
@token_required

def get_port_timing(port):
    try:
        config = load_config(paths.CONFIG_SYSTEM_PATH)
        port_data = config.get(port)

        if not port_data or "timing" not in port_data:
            return jsonify({"error": f"Timingdata ikke funnet for {port}"}), 404

        timing_data = port_data["timing"]
        result = {}

        for direction in ["open", "close"]:
            direction_data = timing_data.get(direction, {})
            result[direction] = {
                "last": direction_data.get("last"),
                "avg": direction_data.get("avg"),
                "t0": direction_data.get("t0"),
                "t1": direction_data.get("t1"),
                "t2": direction_data.get("t2"),
                "history": direction_data.get("history", [])
            }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Intern feil: {str(e)}"}), 500


@timing_routes.route("/timing", methods=["GET"])
@token_required
def get_all_port_timing():
    try:
        config = load_config(paths.CONFIG_SYSTEM_PATH)
        result = {}

        for port in config:
            port_data = config.get(port)
            if not port_data or "timing" not in port_data:
                continue

            timing_data = port_data["timing"]
            result[port] = {}

            for direction in ["open", "close"]:
                direction_data = timing_data.get(direction, {})
                result[port][direction] = {
                    "last": direction_data.get("last"),
                    "avg": direction_data.get("avg"),
                    #"t0": direction_data.get("t0"),
                    #"t1": direction_data.get("t1"),
                    #"t2": direction_data.get("t2"),
                    #"history": direction_data.get("history", [])
                }

        if not result:
            return jsonify({"error": "Ingen timingdata funnet"}), 404

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Intern feil: {str(e)}"}), 500