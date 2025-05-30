# app.py

import os
import atexit
from flask import Flask

from utils.logging.unified_logger import get_logger

from config.config_paths import LOG_DIR
from core import system_init
from core.system import controller
from core.bootstrap import initialize_system_environment
from monitor.system_monitor_task import start_system_monitor_task
from monitor.sensor_monitor_task import run_sensor_monitor_loop
import threading
from routes.api import api


logger = get_logger("system", category="system")


# Flask-app
app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.register_blueprint(api)
#app.register_blueprint(sensor_routes)


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
    system_routes,
    sensor_routes
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
    logger.debug("Starter Flask-applikasjon...")
    logger.info("Initierer system og validerer loggkonfigurasjon...")
    system_init.init()  # Initierer system og validerer logger
    # Start sensor-monitor i bakgrunnen
    threading.Thread(target=run_sensor_monitor_loop, daemon=True).start()
    atexit.register(controller.shutdown)
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
