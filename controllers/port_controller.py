# controllers/port_controller.py

import json
from config.config_paths import CONFIG_SYSTEM_PATH
from core.system import controller


def get_status(port):
    return controller.get_port_status(port)

def open_port(port):
    return controller.open_port(port)

def close_port(port):
    return controller.close_port(port)

def get_timing(port):
    # Returner siste måling for porten (dette er placeholder)
    # Alternativ: les fra config_system.json hvis du ønsker persistens
    return {
        "open_time": None,
        "close_time": None
    }

def get_all_status():
    ports = controller.relay_pins.keys()
    return {port: get_status(port) for port in ports}

def get_timing(port):
    try:
        with open(CONFIG_SYSTEM_PATH) as f:
            config = json.load(f)
        return config.get("timing", {}).get(port, {})
    except:
        return {}