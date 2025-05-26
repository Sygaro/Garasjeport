# app.py

import os
import atexit
from flask import Flask, render_template

from config.config_paths import LOG_DIR
from core.system import controller
from core.bootstrap import initialize_system_environment
from monitor.system_monitor_task import start_system_monitor_task
from routes.api.system_routes import system_routes


# Flask-app
app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
#app.register_blueprint(system_routes)


# Init system
initialize_system_environment()
start_system_monitor_task()

# Ruter
from routes.api import (
    port_routes,
    status_routes,
    config_routes,
    log_routes,
    system_routes
)
from routes.web import web

# Registrer alle blueprints
for bp in [
    port_routes,
    status_routes,
    config_routes,
    log_routes,
    system_routes,
    web,
]:
    app.register_blueprint(bp)

# Helse-endepunkt
@app.route("/health")
def health_check():
    return {"status": "ok", "version": "1.0"}

# Kjør applikasjonen
if __name__ == "__main__":
    print("[APP] Starter Flask-applikasjon...")
    atexit.register(controller.shutdown)
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
