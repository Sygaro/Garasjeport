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
 

# Init systemet
initialize_system_environment()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True


# Registrer alle blueprint-moduler
for bp in [port_routes, status_routes, config_routes, log_routes, web, api]:
    app.register_blueprint(bp)

@app.route("/")
def admin():
    return render_template("admin.html")

@app.route("/api/logs/<logtype>")
def get_log(logtype):
    path = os.path.join(LOG_DIR, f"{logtype}.log")
    try:
        with open(path, "r") as f:
            lines = f.readlines()[-20:]
        return jsonify({"lines": lines})
    except FileNotFoundError:
        return jsonify({"error": "Logg ikke funnet"}), 404

@app.route("/log")
def log_page():
    return render_template("log.html")

@app.route("/admin/config/restore")
def config_restore_page():
    return render_template("restore_config.html")

@app.route("/backup")
def config_backup_page():
    return render_template("backup.html")

@app.route("/help")
def system_doc_page():
    return render_template("help.html")

@app.route("/admin/gpio")
def gpio_ui():
    return render_template("admin_gpio_config.html")

@app.route("/stats")
def stats_page():
    return render_template("stats.html")

# Rute for helse/tilgjengelighet
@app.route("/health")
def health_check():
    return {"status": "ok", "version": "1.0"}


if __name__ == "__main__":
    print("[APP] Starter Flask-applikasjon...")
    # Kjør cleanup() automatisk ved avslutning
    atexit.register(controller.cleanup)
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
