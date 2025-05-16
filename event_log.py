
# Fil: event_log.py
# Strukturert logging til events.log + syslog med robust port-håndtering

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger("event_logger")
handler = logging.FileHandler("logs/events.log", encoding="utf-8")
handler.setFormatter(logging.Formatter("%(message)s"))
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Valgfritt syslog-oppsett
if os.path.exists("/dev/log"):
    try:
        from logging.handlers import SysLogHandler
        syslog = SysLogHandler(address="/dev/log")
        syslog.setFormatter(logging.Formatter("garasjeport: %(message)s"))
        logger.addHandler(syslog)
    except Exception:
        pass

def extract_port(message, data):
    """Prøver å finne port fra melding eller data hvis port=None"""
    if data and isinstance(data, dict):
        if "port" in data:
            return str(data["port"])
    if isinstance(message, str) and "port" in message:
        try:
            parts = message.split("port")
            if len(parts) > 1:
                suffix = parts[1].strip()
                return "port" + suffix.split()[0]
        except Exception:
            pass
    return None

def log_event(event_type, message, port=None, data=None):
    """Logger en strukturert JSON-linje til events.log"""
    port = port or extract_port(message, data)
    entry = {
        "time": datetime.now().isoformat(),
        "type": event_type,
        "message": message,
        "port": port,
        "data": data or {},
    }
    logger.info(json.dumps(entry, ensure_ascii=False))
