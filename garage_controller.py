# Fil: garage_controller.py
# Modul for styring av porter via releer og statusavlesing fra sensorer

# For Raspberry Pi - erstatt med `import RPi.GPIO as GPIO`
try:
    import RPi.GPIO as GPIO
except ImportError:
    # Mock for utvikling uten fysisk Pi
    from unittest import mock
    GPIO = mock.MagicMock()

import time
import logging

class GarageController:
    def __init__(self, config):
        # Last inn rele- og sensor-pinner fra config
        self.relay_pins = config.get("relay_pins", {})
        self.sensor_pins = config.get("sensor_pins", {})

        # Init GPIO
        GPIO.setmode(GPIO.BCM)
        for port_name, pin in self.relay_pins.items():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)  # Start med rele av

        for port_name, sensors in self.sensor_pins.items():
            GPIO.setup(sensors["open"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(sensors["closed"], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        logging.info("GarageController initialisert")

    def open_port(self, port_name):
        """Trigge rele for å åpne/lukke port"""
        pin = self.relay_pins.get(port_name)
        if pin is None:
            logging.warning(f"Ugyldig portnavn: {port_name}")
            return False

        logging.info(f"Åpner port: {port_name}")
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.5)  # Puls
        GPIO.output(pin, GPIO.LOW)
        return True

    def get_status(self, port_name):
        """Returner 'open', 'closed' eller 'unknown' basert på sensor-input"""
        pins = self.sensor_pins.get(port_name)
        if not pins:
            logging.warning(f"Sensorer ikke definert for: {port_name}")
            return "unknown"

        open_state = GPIO.input(pins["open"]) == GPIO.LOW
        closed_state = GPIO.input(pins["closed"]) == GPIO.LOW

        if open_state and not closed_state:
            return "open"
        elif closed_state and not open_state:
            return "closed"
        else:
            return "unknown"

    def cleanup(self):
        """Rydd opp GPIO ved avslutning"""
        GPIO.cleanup()
        logging.info("GPIO ryddet opp")
