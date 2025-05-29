from utils.logging.unified_logger import get_logger
# utils/file_utils.py

import json, os

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Kunne ikke laste JSON-fil: {path} – {e}")

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)