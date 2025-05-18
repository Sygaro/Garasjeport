from flask import Blueprint, jsonify, request
from controllers.port_controller import PortController
from controllers.logger_controller import LoggerController


api = Blueprint("api", __name__)
port_controller = PortController()  # opprett instans
logger_controller = LoggerController()

@api.route("/api/status")
def get_port_status(port):
    return jsonify({"status": port_ctrl.get_status(port)})

@api.route("/api/log")
def get_log():
    logs = logger_controller.get_recent_logs(limit=20)
    return jsonify({"logs": logs})
    

@api.route("/api/toggle", methods=["POST"])
def toggle_port():
    port_controller.toggle_port()
    return jsonify({"success": True})
