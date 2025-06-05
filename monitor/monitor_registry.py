# Filnavn: monitor_registry.py

import threading
from datetime import datetime
from utils.logging.unified_logger import get_logger

# Global registry og mutex for tråd-sikkerhet
_monitor_registry = {}
_registry_lock = threading.Lock()
logger = get_logger("monitor_registry", category="system")

def register_monitor(name: str):
    with _registry_lock:
        if name not in _monitor_registry:
            _monitor_registry[name] = {
                "name": name,
                "registered_at": datetime.now(),
                "last_ping": None,
                "status": "running",
                "started_at": datetime.utcnow().isoformat() + "Z",
                "last_updated": datetime.utcnow().isoformat() + "Z"
                    }
            logger.info(f"Monitor registrert: {name}")
        else:
            logger.debug(f"Monitor allerede registrert: {name}")

def update_ping(name: str):
    with _registry_lock:
        if name in _monitor_registry:
            _monitor_registry[name]["last_ping"] = datetime.now()
            logger.debug(f"Ping mottatt fra monitor: {name}")
        else:
            logger.warning(f"Forsøk på ping fra uregistrert monitor: {name}")

def update_monitor(name):
    if name in _monitor_registry:
        _monitor_registry[name]["last_updated"] = datetime.utcnow().isoformat() + "Z"


def get_registry_status():
    with _registry_lock:
        return {
            name: {
                **info,
                "registered_at": info["registered_at"].isoformat(),
                "last_ping": info["last_ping"].isoformat() if info["last_ping"] else None
            } for name, info in _monitor_registry.items()
        }
