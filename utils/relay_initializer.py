# utils/relay_initializer.py

import pigpio
from utils.pigpio_manager import get_pi
from utils.file_utils import load_json
from config.config_paths import CONFIG_GPIO_PATH

def initialize_relays():
    """
    Setter GPIO-modus og initialverdi for alle relepinner basert på konfig.
    Returnerer relay_pins og relay_config som videre brukes i systemet.
    """
    pi = get_pi()
    config = load_json(CONFIG_GPIO_PATH)

    relay_pins = config.get("relay_pins", {})
    relay_config = config.get("relay_config", {})
    active_state = relay_config.get("active_state", 1)

    for port, pin in relay_pins.items():
        pi.set_mode(pin, pigpio.OUTPUT)
        pi.write(pin, 1 - active_state)  # Sett pin til inaktiv

    return relay_pins, relay_config
