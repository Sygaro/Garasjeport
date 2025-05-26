# routes/api/timing_routes.py

from flask import Blueprint, jsonify
from utils.auth import token_required
from core.system import controller

timing_routes = Blueprint("timing_routes", __name__)

@timing_routes.route("/timing/<port>", methods=["GET"])
@token_required
def get_port_timing(port):
    timing_data = controller.get_timing_data(port)
    if not timing_data:
        return jsonify({"error": f"Timingdata ikke funnet for {port}"}), 404
    return jsonify(timing_data)
