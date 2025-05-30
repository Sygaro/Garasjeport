# routes/api/__init__.py

from flask import Blueprint

api = Blueprint("api", __name__, url_prefix="/api")

# Import all route modules
__all__ = [
    "config_routes",
    "port_routes",
    "status_routes",
    "timing_routes",
    "system_routes",
    "log_routes",
    "sensor_routes"
]

from .config_routes import config_routes
from .port_routes import port_routes
from .status_routes import status_routes
from .timing_routes import timing_routes
from .system_routes import system_routes
from .log_routes import log_routes
from .sensor_routes import sensor_routes

api.register_blueprint(config_routes)
api.register_blueprint(port_routes)
api.register_blueprint(status_routes)
api.register_blueprint(timing_routes)
api.register_blueprint(system_routes)
api.register_blueprint(log_routes)
api.register_blueprint(sensor_routes)

