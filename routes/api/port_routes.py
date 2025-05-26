# routes/api/port_routes.py

from flask import Blueprint, jsonify, request
from utils.auth import token_required
from core.system import controller

port_routes = Blueprint("port_routes", __name__)

@port_routes.route("/port/<port>/open", methods=["POST"])
@token_required
def api_open_port(port):
    try:
        result = controller.open_port(port)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@port_routes.route("/port/<port>/close", methods=["POST"])
@token_required
def api_close_port(port):
    try:
        result = controller.close_port(port)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@port_routes.route("/port/<port>/stop", methods=["POST"])
@token_required
def api_stop_port(port):
    try:
        result = controller.stop_port(port)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
