# routes/system_routes.py
import datetime, os, json

from flask import Blueprint, jsonify, request
from utils.auth import token_required
from utils.config_loader import load_config
from config import config_paths as paths
from utils.system_monitor import get_system_status, check_thresholds_and_log, run_system_health_check



system_routes = Blueprint("system_routes", __name__, url_prefix="/api/system")


@system_routes.route("/pigpio", methods=["GET"])
@token_required
def get_pigpio_status():
    try:
        with open(paths.PIGPIO_STATUS_PATH, "r") as f:
            data = f.read()
        return jsonify(json.loads(data))
    except Exception as e:
        return jsonify({"error": "Statusfil ikke funnet", "details": str(e)}), 404


@system_routes.route("/bootstrap_status", methods=["GET"])
@token_required
def get_bootstrap_status():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fallback_response = {
        "bootstrap_time": None,
        "pigpiod_expected": None,
        "config_validated": None,
        "version_backend": None,
        "version_frontend": None,
        "version_mismatch": True,
        "fallback": True,
        "message": "Ingen runtime-status tilgjengelig – dette er cached versjon fra oppstart",
        "timestamp": now
    }

    try:
        with open(paths.BOOTSTRAP_STATUS_PATH, "r") as f:
            data = json.load(f)
            version_backend = data.get("version") or "ukjent"

        version_frontend = "ukjent"
        try:
            with open(os.path.join(paths.STATUS_DIR, "frontend_version.json")) as vf:
                version_frontend = json.load(vf).get("frontend_version") or "ukjent"
        except:
            pass

        mismatch = (
            version_backend == "ukjent" or
            version_frontend == "ukjent" or
            version_backend != version_frontend
        )

        return jsonify({
            **data,
            "version_backend": version_backend,
            "version_frontend": version_frontend,
            "version_mismatch": mismatch,
            "fallback": False,
            "timestamp": now
        })

    except Exception:
        return jsonify(fallback_response), 200


@system_routes.route("/version_report", methods=["POST"])
@token_required
def report_frontend_version():
    data = request.get_json()
    version = data.get("frontend_version")
    if version:
        with open(os.path.join(paths.STATUS_DIR, "frontend_version.json"), "w") as f:
            json.dump({"frontend_version": version}, f)
        return jsonify({"message": "Frontend-versjon lagret", "version": version})
    else:
        return jsonify({"error": "frontend_version ikke angitt"}), 400


# routes/api/system_routes.py

@system_routes.route("/system/rpi_status", methods=["GET"])
@token_required
def get_rpi_status():
    try:
        status = get_system_status()
        warnings = check_thresholds_and_log(status)
        return jsonify({
            "status": status,
            "warnings": warnings
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@system_routes.route("/system/health", methods=["GET"])
@token_required
def get_system_health():
    result = run_system_health_check()
    result["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify(result)