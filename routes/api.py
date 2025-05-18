# routes/api.py

from flask import Blueprint, jsonify, request
from core.system import controller
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
    
@api.route("/port/<port>/open", methods=["POST"])
def api_open_port(port):
    result = controller.activate_port(port, "open")
    return jsonify(result)

@api.route("/port/<port>/close", methods=["POST"])
def api_close_port(port):
    result = controller.activate_port(port, "close")
    return jsonify(result)
