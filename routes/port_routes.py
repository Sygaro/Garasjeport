# ==========================================
# Filnavn: port_routes.py
# API-endepunkter for portstyring (puls/motor)
# ==========================================

from flask import Blueprint, jsonify, request
from controllers.garage import handle_port_pulse
from controllers.status import get_port_status

port_routes = Blueprint("port_routes", __name__)

@port_routes.route("/api/pulse/<port>", methods=["POST"])
def pulse_port(port):
    """
    Sender puls til valgt port via GPIO-relé.
    Bruker source fra request body.
    """
    if port not in ['port1', 'port2']:
        return jsonify({"error": "Ugyldig portnavn"}), 400

    data = request.get_json(force=True, silent=True) or {}
    source = data.get("source", "api")

    result = handle_port_pulse(port, source)

    if not result["success"]:
        return jsonify(result), 409

    return jsonify(result), 200
