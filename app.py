# ==========================================
# Filnavn: app.py
# Starter Flask-app og registrerer Blueprints
# ==========================================

from flask import Flask, jsonify, request, render_template

from routes.port_routes import port_routes
from routes.status_routes import status_routes
from routes.config_routes import config_routes
from routes.log_routes import log_routes
from core.bootstrap import init_environment

# Kjør init ved app-start
init_environment()




app = Flask(__name__)
app.register_blueprint(port_routes)
app.register_blueprint(status_routes)
app.register_blueprint(config_routes)
app.register_blueprint(log_routes)


@app.route("/")
def index():
    return "<h3>Garage API er aktiv (modulær versjon)</h3>"

@app.route("/admin/config")
def config_editor():
    return render_template("admin_config_editor.html")

@app.route("/stats")
def stats_page():
    return render_template("stats.html")

@app.route("/api/logs/<logtype>")
def get_log(logtype):
    log_path = f"logs/{logtype}.log"
    try:
        with open(log_path, 'r') as f:
            lines = f.readlines()[-20:]
        return jsonify({"lines": lines})
    except:
        return jsonify({"error": "Logg ikke funnet"}), 404

@app.route("/log")
def log_page():
    return render_template("log.html")


@app.route("/api/config", methods=["GET"])
def get_config():
    with open("config.json") as f:
        config = json.load(f)
    return jsonify(config)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
