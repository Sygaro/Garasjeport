# routes/api.py

from flask import Blueprint, jsonify, request
from core.system import controller
from utils.auth import token_required
from controllers.logger_controller import logger_controller
from controllers.port_controller import (
    open_port, close_port,
    get_status, get_all_status,
    get_timing
)

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/status", methods=["GET"])
@token_required
def api_all_status():
    """Henter status for alle porter"""
    return jsonify(get_all_status())


@api.route("/status/<port>", methods=["GET"])
@token_required
def api_single_status(port):
    """Henter status for én port"""
    return jsonify({port: get_status(port)})


@api.route("/port/<port>/open", methods=["POST"])
@token_required
def api_open_port(port):
    """Åpner valgt port"""
    result = open_port(port)
    return jsonify(result)


@api.route("/port/<port>/close", methods=["POST"])
@token_required
def api_close_port(port):
    """Lukker valgt port"""
    result = close_port(port)
    return jsonify(result)

@api.route("/port/<port>/stop", methods=["POST"])
@token_required
def api_stop_port(port):
    """
    Stopper porten hvis den er i bevegelse (begge sensorer inaktive).
    """
    result = controller.stop_port(port)
    return jsonify(result)



@api.route("/timing/<port>", methods=["GET"])
@token_required
def api_get_timing(port):
    """Henter siste åpne/lukke tider for gitt port"""
    timing = get_timing(port)
    return jsonify({port: timing})


@api.route("/log", methods=["GET"])
@token_required
def api_get_log():
    """Henter siste linjer fra aktivitetsloggen"""
    logs = logger_controller.get_recent_logs(limit=100)
    return jsonify({"logs": logs})
