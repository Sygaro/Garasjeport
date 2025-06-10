# app.py

from flask import Flask
from routes.api import api
from routes.api.port_routes import port_routes
from routes.api.status_routes import status_routes
from routes.api.config_routes import config_routes
from routes.api.log_routes import log_routes
from routes.api.system_routes import system_routes
from routes.api.sensor_routes import sensor_routes
from routes.api.bootstrap_routes import bootstrap_routes
from routes.web import web
# Opprett Flask-app
app = Flask(__name__)


# Registrer alle blueprints
for bp in [api, port_routes, status_routes, config_routes, log_routes, system_routes, sensor_routes, bootstrap_routes, web]:
    app.register_blueprint(bp)

# Ekstra direkte-ruter om ønskelig
@app.route("/health")
def health_check():
    return {"status": "ok", "version": "1.0"}


# Importer ALLE routes slik at de blir en del av appen
# (NB: Opprett gjerne __init__.py i routes/-mappen om det mangler)
try:
    from routes.web import *
except ImportError:
    pass

try:
    from routes.api import *
except ImportError:
    pass

# Her kan du legge inn custom errorhandlers og hooks hvis ønskelig
# f.eks. @app.errorhandler(404)
# def not_found(e):
#     return "Not found", 404
