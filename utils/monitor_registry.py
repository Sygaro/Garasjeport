# monitor_registry.py

import time
from typing import Dict, Any, Optional
from utils.logging.unified_logger import get_logger

logger = get_logger(name="monitor_registry", category="system", source="registry")

_registry: Dict[str, Dict[str, Any]] = {}

def register_monitor(name: str, status: str = "REGISTERED", metadata: Optional[dict] = None):
    """
    Registrerer eller oppdaterer en monitor i registeret.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    _registry[name] = {
        "status": status,
        "timestamp": timestamp,
        "metadata": metadata or {}
    }
    logger.info(f"Monitor '{name}' registrert med status '{status}' og metadata: {_registry[name]['metadata']}")

def update_monitor_status(name: str, status: str):
    """
    Oppdaterer statusen til en eksisterende monitor.
    """
    if name in _registry:
        _registry[name]["status"] = status
        _registry[name]["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        logger.debug(f"Monitor '{name}' oppdatert til status '{status}'")
    else:
        logger.warning(f"Forsøk på å oppdatere ukjent monitor '{name}' med status '{status}'")

def get_registry_status() -> Dict[str, Dict[str, Any]]:
    """
    Returnerer hele monitor-registeret.
    """
    return _registry.copy()
