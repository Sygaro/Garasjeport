# utils/file_utils.py

import json, os

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)