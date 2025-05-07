
# Fil: event_log.py
# Enkel JSON-basert loggfunksjon for systemhendelser

import os
import json
from datetime import datetime

LOGGFIL = "logs/events.log"

def log_event(type, message, port=None, data=None):
    os.makedirs("logs", exist_ok=True)
    entry = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "type": type,
        "message": message
    }
    if port:
        entry["port"] = port
    if data:
        entry["data"] = data

    with open(LOGGFIL, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
