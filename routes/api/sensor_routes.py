from utils.logging.unified_logger import get_logger
import os
import re
import json
from flask import Blueprint, jsonify, request
from utils.auth import token_required
from config import config_paths
from monitor.environment_manager import EnvironmentSensorManager


sensor_api_logger = get_logger("sensor_routes", category="system")

sensor_routes = Blueprint("sensor_routes", __name__, url_prefix="/sensors/environment")
sensor_manager = EnvironmentSensorManager()

@sensor_routes.route("/latest", methods=["GET"])
@token_required
def get_latest_sensor_data():
    try:
        path = config_paths.STATUS_SENSOR_ENV_PATH
        if not os.path.exists(path):
            return jsonify({"error": "Ingen sensordata funnet"}), 404

        with open(path, "r") as f:
            data = json.load(f)
        return jsonify({"sensors": data})

    except Exception as e:
        sensor_api_logger.error("sensor_routes", f"Feil i /sensors/environment/latest: {str(e)}")
        return jsonify({"error": "Kunne ikke hente sensorstatus"}), 500

@sensor_routes.route("/history", methods=["GET"])
@token_required
def get_sensor_history():
    path = config_paths.LOG_SENSOR_ENV_PATH
    sensor_filter = request.args.get("sensor")
    limit = int(request.args.get("limit", 50))

    if not os.path.exists(path):
        return jsonify({"error": "Sensor-loggfil ikke funnet"}), 404

    try:
        with open(path, "r") as f:
            lines = f.readlines()

        pattern = re.compile(r"^(.*?)\s+\[.*?\]\s+.*?:\s*(\w+):\s*Temp: ([\d.]+)\u00b0C.*Hum: ([\d.]+)%.*Press: ([\d.]+) hPa")
        entries = []
        for line in reversed(lines):
            match = pattern.search(line)
            if match:
                timestamp, sensor_id, temp, hum, press = match.groups()
                if sensor_filter and sensor_id != sensor_filter:
                    continue
                entries.append({
                    "timestamp": timestamp,
                    "sensor": sensor_id,
                    "temperature": float(temp),
                    "humidity": float(hum),
                    "pressure": float(press)
                })
            if len(entries) >= limit:
                break

        return jsonify({"history": list(reversed(entries))})

    except Exception as e:
        sensor_api_logger.error("sensor_routes", f"Feil i /sensors/environment/history: {str(e)}")
        return jsonify({"error": str(e)}), 500

@sensor_routes.route("/averages", methods=["GET"])
@token_required
def get_sensor_averages():
    path = config_paths.LOG_SENSOR_ENV_AVERAGES_PATH
    sensor_filter = request.args.get("sensor")
    limit = int(request.args.get("limit", 24))

    if not os.path.exists(path):
        return jsonify({"error": "Snittlogg ikke funnet"}), 404

    try:
        with open(path, "r") as f:
            lines = f.readlines()

        entries = []
        for line in reversed(lines):
            try:
                data = json.loads(line)
                if sensor_filter and data.get("sensor") != sensor_filter:
                    continue
                entries.append(data)
            except Exception:
                continue
            if len(entries) >= limit:
                break

        return jsonify({"averages": list(reversed(entries))})

    except Exception as e:
        sensor_api_logger.error("sensor_routes", f"Feil i /sensors/environment/averages: {str(e)}")
        return jsonify({"error": str(e)}), 500

@sensor_routes.route("/logging", methods=["GET"])
@token_required
def get_logging_status():
    try:
        return jsonify({
            "logging_enabled": sensor_manager.is_logging_enabled(),
            "log_interval_seconds": sensor_manager.log_interval
        })
    except Exception as e:
        sensor_api_logger.error("sensor_routes", f"Feil i GET /sensors/environment/logging: {str(e)}")
        return jsonify({"error": str(e)}), 500

@sensor_routes.route("/logging", methods=["POST"])
@token_required
def set_logging_status():
    try:
        body = request.get_json()
        if "enabled" in body:
            sensor_manager.set_logging_enabled(bool(body["enabled"]))
        if "interval" in body:
            sensor_manager.set_log_interval(int(body["interval"]))

        return jsonify({
            "message": "Oppdatert logging",
            "logging_enabled": sensor_manager.is_logging_enabled(),
            "log_interval_seconds": sensor_manager.log_interval
        })
    except Exception as e:
        sensor_api_logger.error("sensor_routes", f"Feil i POST /sensors/environment/logging: {str(e)}")
        return jsonify({"error": str(e)}), 500
