from utils.logging.unified_logger import get_logger
# routes/system_routes.py
import datetime, os, json

from flask import Blueprint, jsonify, request
from utils.auth import token_required
#from utils.config_loader import load_config
from config import config_paths as paths
from monitor.system_monitor import get_system_status, check_thresholds_and_log, run_system_health_check, get_diagnostics
from monitor.monitor_registry import get_registry_status


system_routes = Blueprint("system_routes", __name__, url_prefix="/system")


@system_routes.route("/pigpio", methods=["GET"])
@token_required
def get_pigpio_status():
    try:
        with open(paths.STATUS_PIGPIO_PATH, "r") as f:
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
        with open(paths.STATUS_BOOTSTRAP_PATH, "r") as f:
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


# routes/api/system_routes.py

@system_routes.route("/rpi_status", methods=["GET"])
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


@system_routes.route("/health", methods=["GET"])
@token_required
def get_system_health():
    result = run_system_health_check()
    result["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify(result)


@system_routes.route("/rpi_diagnostics", methods=["GET"])
@token_required
def rpi_diagnostics():
    try:
        status = get_system_status()
        report = get_diagnostics(status)

        total = len(report)
        warnings = [
            r for r in report
            if any(neg in r for neg in ["overstiger", "under minimum"])
            or r.strip().startswith("Systemoppdateringer tilgjengelig")
        ]
        count_warnings = len(warnings)

        if count_warnings == 0:
            summary = "System OK – ingen advarsler"
        elif count_warnings <= total / 2:
            summary = f"Delvis OK – {count_warnings} av {total} forhold har avvik"
        else:
            summary = f"Alvorlig – {count_warnings} av {total} forhold har avvik"

        return jsonify({
            "summary": summary,
            "diagnostics": report,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@system_routes.route("/monitors", methods=["GET"])
@token_required
def get_monitors_status():
    """
    Returnerer status for alle aktive monitorer.
    """
    status = get_registry_status()
    return jsonify(status)
