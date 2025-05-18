# routes/api.py

from flask import Blueprint, jsonify, request
from controllers.port_controller import (
    get_status, open_port, close_port, get_timing, get_all_status
)
from controllers.logger_controller import logger_controller

api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/status/<port>")
def api_status(port):
    return jsonify({"port": port, "status": get_status(port)})

@api.route("/status")
def api_all_status():
    return jsonify(get_all_status())

@api.route("/open/<port>", methods=["POST"])
def api_open_port(port):
    result = open_port(port)
    return jsonify(result)

@api.route("/close/<port>", methods=["POST"])
def api_close_port(port):
    result = close_port(port)
    return jsonify(result)

@api.route("/timing/<port>")
def api_port_timing(port):
    return jsonify(get_timing(port))

@api.route("/log")
def api_get_log():
    logs = logger_controller.get_recent_logs(limit=20)
    return jsonify({"logs": logs})

@api.route("/api/timing/<port>")
def api_get_timing(port):
    timing = controller.get_port_timing(port)
    return jsonify(timing)
