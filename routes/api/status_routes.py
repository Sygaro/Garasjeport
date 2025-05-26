# ==========================================
# Filnavn: status_routes.py
# API-endepunkt for portstatus
# ==========================================

from flask import Blueprint, jsonify
from core.system import controller
from utils.auth import token_required


status_routes = Blueprint("status_routes", __name__)

@status_routes.route("/status/<port>", methods=["GET"])
@token_required
def port_status(port):
    """
    Returnerer status for spesifisert port.
    """
    valid_ports = controller.get_ports()
    if port not in valid_ports:
        return jsonify({"error": f"Ugyldig portnavn: {port}"}), 400

    status = controller.get_current_status(port)
    return jsonify({
        "port": port,
        "status": status
    }), 200


@status_routes.route("/status", methods=["GET"])
@token_required
def all_status():
    """
    Returnerer status for alle porter.
    """
    return jsonify(controller.get_all_status()), 200
