# routes/api/__init__.py

from .port_routes import port_routes
from .status_routes import status_routes
from .config_routes import config_routes
from .log_routes import log_routes
from .system_routes import system_routes

__all__ = [
    "port_routes",
    "status_routes",
    "config_routes",
    "log_routes",
    "system_routes"
]
