# utils/log_utils.py

import os

def parse_log_file(filepath, limit=100):
    """
    Leser siste X linjer fra loggfil og returnerer liste med:
    [{"time": "...", "message": "..."}]
    """
    if not os.path.exists(filepath):
        return []

    with open(filepath, "r") as f:
        lines = f.readlines()[-limit:]

    entries = []
    for line in lines:
        time_part = line[:19] if len(line) > 20 else ""
        message = line[20:].strip() if len(line) > 20 else line.strip()
        entries.append({
            "time": time_part,
            "message": message
        })

    return entries
