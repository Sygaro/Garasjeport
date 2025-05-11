"""
🔧 config.py: Felles funksjoner for konfigurasjon
✨ Innhold:
load_config() – leser config.json
save_config(data) – lagrer ny konfig
Valgfritt: get_value(key, default) hvis du ønsker nøkkelhenting med fallback
"""

import json
import os

CONFIG_PATH = "config.json"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Konfigurasjonsfilen '{CONFIG_PATH}' finnes ikke.")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config_data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)
