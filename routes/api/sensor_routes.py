# routes/api/sensor_routes.py

import os
import re
import json
from datetime import datetime
from flask import Blueprint, jsonify, request
from utils.auth import token_required
from config import config_paths
from utils.garage_logger import get_logger

logger = get_logger("sensor_api")
sensor_routes = Blueprint("sensor_routes", __name__, url_prefix="/sensors")

@sensor_routes.route("/latest", methods=["GET"])
@token_required
def get_latest_sensor_data():
    """
    Returnerer sist målte sensorverdier (fra sensor_data.json).
    """
    try:
        path = config_paths.SENSOR_STATUS_PATH
        if not os.path.exists(path):
            return jsonify({"error": "Ingen sensordata funnet"}), 404

        with open(path, "r") as f:
            data = json.load(f)
        return jsonify({
            "sensors": data
        })

    except Exception as e:
        logger.log_error("sensor_routes", f"Feil i /sensors/latest: {str(e)}")
        return jsonify({"error": "Kunne ikke hente sensorstatus"}), 500

@sensor_routes.route("/history", methods=["GET"])
@token_required
def get_sensor_history():
    """
    Returnerer siste målinger fra sensor-loggfilen.
    Parametre:
    - sensor: ID på sensor (valgfritt)
    - since: tidspunkt (format: YYYY-MM-DD HH:MM:SS, valgfritt)
    - limit: maks antall rader etter filter (default: 50)
    """
    path = config_paths.SENSOR_LOG_PATH
    sensor_filter = request.args.get("sensor")
    since_str = request.args.get("since")
    limit = int(request.args.get("limit", 50))

    if not os.path.exists(path):
        return jsonify({"error": "Sensor-loggfil ikke funnet"}), 404

    since_dt = None
    if since_str:
        try:
            since_dt = datetime.strptime(since_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify({"error": "Ugyldig format for 'since'. Bruk YYYY-MM-DD HH:MM:SS"}), 400

    try:
        with open(path, "r") as f:
            lines = f.readlines()

        pattern = re.compile(r"^(.*?)\s+\[.*?\]\s+.*?:\s*(\w+):\s*Temp: ([\d.]+)\u00b0C.*Hum: ([\d.]+)%.*Press: ([\d.]+) hPa")
        entries = []
        for line in reversed(lines):
            match = pattern.search(line.strip())
            if match:
                timestamp, sensor_id, temp, hum, press = match.groups()

                if sensor_filter and sensor_id != sensor_filter:
                    continue

                if since_dt:
                    log_dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S,%f")
                    if log_dt < since_dt:
                        continue

                entries.append({
                    "timestamp": timestamp.split(",")[0],
                    "sensor": sensor_id,
                    "temperature": float(temp),
                    "humidity": float(hum),
                    "pressure": float(press)
                })

            if len(entries) >= limit:
                break

        return jsonify({
            "history": list(reversed(entries))
        })

    except Exception as e:
        logger.log_error("sensor_routes", f"Feil i /sensors/history: {str(e)}")
        return jsonify({"error": str(e)}), 500
