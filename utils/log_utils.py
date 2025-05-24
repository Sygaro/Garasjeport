# utils/log_utils.py

import os
import datetime
import shutil
from config import config_paths as paths
from utils.config_loader import load_logging_config

# Konfig
logging_config = load_logging_config()
enabled_logs = logging_config["enabled_logs"]
max_kb = logging_config["max_file_size_kb"]

def _rotate_log_file(path):
    """
    Flytter en overfylt loggfil til /logs/archived/YYYY-MM-DD/
    """
    if not os.path.exists(path):
        return

    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    archive_dir = os.path.join(paths.ARCHIVE_DIR, date_str)
    os.makedirs(archive_dir, exist_ok=True)

    filename = os.path.basename(path)
    archived_path = os.path.join(archive_dir, filename)

    shutil.move(path, archived_path)
    print(f"[LOG ROTATE] {filename} flyttet til {archived_path}")

def log_event(path: str, msg: str):
    """
    Logger en linje til fil – hvis aktivert og under max størrelse.
    """
    log_type = os.path.splitext(os.path.basename(path))[0]
    if not enabled_logs.get(log_type, False):
        return

    os.makedirs(paths.LOG_DIR, exist_ok=True)

    if os.path.exists(path) and os.path.getsize(path) > max_kb * 1024:
        _rotate_log_file(path)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(path, "a") as f:
        f.write(f"{timestamp} | {msg}\n")


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
