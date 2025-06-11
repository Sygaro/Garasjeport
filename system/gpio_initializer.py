from utils.logging.unified_logger import get_logger
#import json
import pigpio
from utils.pigpio_manager import get_pi
from utils.file_utils import read_json
from config.config_paths import CONFIG_GPIO_PATH

def configure_gpio_pins(sensor_pins, pull, pi):
    pull_mode = {
        "up": pigpio.PUD_UP,
        "down": pigpio.PUD_DOWN,
        "off": pigpio.PUD_OFF
    }.get(pull.lower(), pigpio.PUD_OFF)

    for port, sensors in sensor_pins.items():
        for sensor_type, gpio in sensors.items():
            pi.set_mode(gpio, pigpio.INPUT)
            pi.set_pull_up_down(gpio, pull_mode)

def initialize_gpio():
    """
    Laster konfigurasjon fra fil og kaller configure_gpio_pins med riktige parametre.
    """
    config = read_json(CONFIG_GPIO_PATH)

    sensor_pins = config.get("sensor_pins", {})
    relay_pins = config.get("relay_pins", {})
    relay_config = config.get("relay_config", {})
    sensor_config = config.get("sensor_config", {})

    pull = sensor_config.get("pull", "up")
    pi = get_pi()

    configure_gpio_pins(sensor_pins=sensor_pins, pull=pull, pi=pi)