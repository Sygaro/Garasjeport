# ==========================================
# Filnavn: config.py
# Håndterer lasting og lagring av config.json
# ==========================================

import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')

def load_config() -> dict:
    """
    Leser inn config.json og returnerer som ordbok.
    """
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def save_config(config: dict):
    """
    Lagrer konfigurasjon til config.json.
    """
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
