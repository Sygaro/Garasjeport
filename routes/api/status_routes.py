# ==========================================
# Filnavn: status_routes.py
# API-endepunkt for portstatus
# ==========================================

from flask import Blueprint, jsonify
from controllers.status import get_port_status

status_routes = Blueprint("status_routes", __name__)

@status_routes.route("/api/status/<port>", methods=["GET"])
def port_status(port):
    """
    Returnerer status for spesifisert port.
    """
    if port not in ['port1', 'port2']:
        return jsonify({"error": "Ugyldig portnavn"}), 400

    status = get_port_status(port)
    return jsonify({
        "port": port,
        "status": status
    }), 200
