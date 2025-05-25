# app.py

import os, atexit

from flask import Flask, jsonify, request, render_template
from datetime import datetime

from core.bootstrap import initialize_system_environment
from core.system import controller

from routes.port_routes import port_routes
from routes.status_routes import status_routes
from routes.config_routes import config_routes
from routes.log_routes import log_routes
from routes.web import web
from routes.api import api

from config.config_paths import LOG_DIR
from core.garage_controller import GarageController
from monitor.system_monitor_task import start_system_monitor_task


# Init systemet
initialize_system_environment()
start_system_monitor_task()

app = Flask(__name__)

app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True


# Registrer alle blueprint-moduler
for bp in [port_routes, status_routes, config_routes, log_routes, web, api]:
    app.register_blueprint(bp)

print("[RUTER]")
print(app.url_map)

# Rute for helse/tilgjengelighet
@app.route("/health")
def health_check():
    return {"status": "ok", "version": "1.0"}


if __name__ == "__main__":
    print("[APP] Starter Flask-applikasjon...")
    # Kjør cleanup() automatisk ved avslutning
    atexit.register(controller.shutdown)
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
