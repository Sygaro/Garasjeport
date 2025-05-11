import logging
import logging.handlers
import json
from datetime import datetime

logger = logging.getLogger("event_logger")
logger.setLevel(logging.INFO)

# Logg til lokal fil
file_handler = logging.FileHandler("logs/events.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(file_handler)

# Forsøk syslog
try:
    syslog_handler = logging.handlers.SysLogHandler(address="/dev/log")
    syslog_format = logging.Formatter('%(asctime)s garasjeport: %(message)s', datefmt='%b %d %H:%M:%S')
    syslog_handler.setFormatter(syslog_format)
    logger.addHandler(syslog_handler)
except Exception as e:
    print(f"⚠️ Syslog ikke tilgjengelig: {e}")

def log_event(event_type, message, port=None, data=None):
    event = {
        "time": datetime.now().isoformat(),
        "type": event_type,
        "message": message,
        "port": port,
        "data": data or {}
    }
    try:
        logger.info(json.dumps(event, ensure_ascii=False))
    except Exception as e:
        print(f"Feil ved logging: {e}")
