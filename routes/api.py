# routes/api.py

import datetime, os

from flask import Blueprint, jsonify, request, Response
from core.system import controller
from config import config_paths as paths
from utils.auth import token_required
from utils.config_loader import load_config
from utils.system_monitor import get_system_status, check_thresholds_and_log
from config import config_paths as paths
from controllers.logger_controller import logger_controller
from utils.garage_logger import GarageLogger
from controllers.port_controller import (
    open_port, close_port,
    get_status, get_all_status,
    get_timing
)

VALID_LOGS = {
    "status": paths.STATUS_LOG,
    "error": paths.ERROR_LOG,
    "activity": paths.ACTIVITY_LOG,
    "timing": paths.TIMING_LOG,
    "bootstrap": paths.BOOTSTRAP_LOG
}

logger = GarageLogger()

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/status", methods=["GET"])
@token_required
def api_all_status():
    """Henter status for alle porter"""
    return jsonify(get_all_status())


@api.route("/status/<port>", methods=["GET"])
@token_required
def api_single_status(port):
    """Henter status for én port"""
    return jsonify({port: get_status(port)})


@api.route("/port/<port>/open", methods=["POST"])
@token_required
def api_open_port(port):
    """Åpner valgt port"""
    result = open_port(port)
    return jsonify(result)


@api.route("/port/<port>/close", methods=["POST"])
@token_required
def api_close_port(port):
    """Lukker valgt port"""
    result = close_port(port)
    return jsonify(result)

@api.route("/port/<port>/stop", methods=["POST"])
@token_required
def api_stop_port(port):
    """
    Stopper porten hvis den er i bevegelse (begge sensorer inaktive).
    """
    result = controller.stop_port(port)
    return jsonify(result)


@api.route("/log", methods=["GET"])
@token_required
def api_get_log():
    """Henter siste linjer fra aktivitetsloggen"""
    logs = logger_controller.get_recent_logs(limit=100)
    return jsonify({"logs": logs})


@api.route("/timing/<port>", methods=["GET"])
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


@api.route("/system/pigpio", methods=["GET"])
@token_required
def get_pigpio_status():
    try:
        with open(paths.PIGPIO_STATUS_PATH, "r") as f:
            data = f.read()
        return Response(data, mimetype="application/json")
    except FileNotFoundError:
        return jsonify({"error": "Statusfil ikke funnet"}), 404

@api.route("/system/health", methods=["GET"])
@token_required
def get_system_health():
    from core.system import controller
    from config import config_paths as paths
    import json
    print("[DEBUG] relay_control.pigpio_connected =",
      controller.relay_control.pigpio_connected)

    result = {
        "system_ok": True,
        "checks": {
            "pigpiod": False,
            "sensor_monitor": False,
            "gpio_ready": False
        },
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Check pigpiod
    try:
        with open(paths.PIGPIO_STATUS_PATH, "r") as f:
            status_data = json.load(f)
            result["checks"]["pigpiod"] = status_data.get("pigpiod_running", False)
    except:
        result["checks"]["pigpiod"] = False

    # Check sensor monitor
    result["checks"]["sensor_monitor"] = controller.sensor_monitor is not None

    # Check GPIO / pigpio lib
    try:
        result["checks"]["gpio_ready"] = controller.relay_control.pigpio_connected
    except:
        result["checks"]["gpio_ready"] = False

    # System status
    result["system_ok"] = all(result["checks"].values())
    return jsonify(result)

@api.route("/system/bootstrap_status", methods=["GET"])
@token_required
def get_bootstrap_status():
    import json
    import datetime
    from config import config_paths as paths

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
            version_backend = data.get("version")
            if not version_backend:
                version_backend = "ukjent"


        version_frontend = None
        try:
            with open(paths.FRONTEND_VERSION_PATH) as vf:
                version_frontend = json.load(vf).get("frontend_version", "ukjent")
        except:
            version_frontend = "ukjent"

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
    
@api.route("/system/version_report", methods=["POST"])
@token_required
def report_frontend_version():
    import json
    from flask import request
    from config import config_paths as paths

    data = request.get_json()
    version = data.get("frontend_version")

    if not version:
        return jsonify({"error": "frontend_version mangler"}), 400

    os.makedirs(paths.STATUS_DIR, exist_ok=True)
    with open(os.path.join(paths.STATUS_DIR, "frontend_version.json"), "w") as f:
        json.dump({"frontend_version": version}, f)

    return jsonify({"message": "Frontend-versjon lagret", "version": version}), 200

from utils.system_monitor import get_system_status, check_thresholds_and_log

@api.route("/system/rpi_status", methods=["GET"])
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
    
@api.route("/logs", methods=["GET"])
@token_required
def list_log_files():
    """
    Returnerer alle tilgjengelige loggtyper som API-et støtter.
    """
    return jsonify({
        "available_logs": list(VALID_LOGS.keys())
    })

    
@api.route("/logs/<logtype>", methods=["GET"])
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
        print(f"[DEBUG] Query param 'lines': {request.args.get('lines')} → parsed: {lines_requested}")
        logger.log_debug("api", f"lines param: {request.args.get('lines')} → parsed: {lines_requested}")

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
        return jsonify({"error": "Loggfil ikke funnet"}), 404
    
    logger.log_debug("api", f"lines param: {request.args.get('lines')} → parsed: {lines_requested}")
