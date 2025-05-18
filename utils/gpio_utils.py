# utils/gpio_utils.py

def get_gpio_info(gpio_config):
    """
    Returnerer GPIO-status til bruk i admin_ports.html.
    Inneholder:
    - available: liste med dicts over BCM og fysisk pin
    - used: liste over BCM-pinner som allerede er i bruk
    """
    used = set()
    available = []

    # Samle alle brukte pinner
    for pin in gpio_config.get("relay_pins", {}).values():
        used.add(pin)

    for sensors in gpio_config.get("sensor_pins", {}).values():
        used.add(sensors.get("open"))
        used.add(sensors.get("closed"))

    # En forenklet mapping BCM → fysisk pin (kan utvides)
    bcm_to_pin = {
        2: 3, 3: 5, 4: 7, 5: 29, 6: 31, 7: 26,
        8: 24, 9: 21, 10: 19, 11: 23, 12: 32,
        13: 33, 14: 8, 15: 10, 16: 36, 17: 11,
        18: 12, 19: 35, 20: 38, 21: 40, 22: 15,
        23: 16, 24: 18, 25: 22, 26: 37, 27: 13
    }

    for bcm, pin in bcm_to_pin.items():
        available.append({"bcm": bcm, "pin": pin})

    return {
        "used": list(used),
        "available": available
    }
