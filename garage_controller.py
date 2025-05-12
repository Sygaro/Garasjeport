
# Fil: garage_controller.py
# Modul for portkontroll: åpne/lukke porter, lese status, og måle bevegelsestid

import time
import RPi.GPIO as GPIO
from event_log import log_event

class GarageController:
    def __init__(self, config):
        self.config = config
        self.relay_pins = config.get("relay_pins", {})
        self.sensor_pins = config.get("sensor_pins", {})

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for pin in self.relay_pins.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        for port, sensors in self.sensor_pins.items():
            for sensor_pin in sensors.values():
                GPIO.setup(sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def cleanup(self):
        GPIO.cleanup()

    def open_port(self, port):
        pin = self.relay_pins.get(port)
        if pin is None:
            log_event("error", f"Ugyldig portnavn: {port}")
            return False

        log_event("action", f"Sender åpen/lukk-impuls til {port}", data={"gpio": pin})
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(self.config.get("relay_pulse_length", 0.5))
        GPIO.output(pin, GPIO.LOW)
        return True

    def get_port_status(self, port):
        pins = self.sensor_pins.get(port)
        if not pins:
            return "ukjent"

        open_state = GPIO.input(pins.get("open"))
        closed_state = GPIO.input(pins.get("closed"))

        if open_state and closed_state:
            return "sensorfeil"
        elif open_state:
            return "åpen"
        elif closed_state:
            return "lukket"
        else:
            return "ukjent"

    def maal_aapnetid(self, port, timeout=60):
        """Måler tid fra port starter åpning til åpen-sensor er aktiv."""
        sensors = self.sensor_pins.get(port)
        if not sensors:
            return None

        status = self.get_port_status(port)
        if status == "åpen":
            log_event("info", f"{port} er allerede åpen")
            return None

        self.open_port(port)
        start = time.time()

        while time.time() - start < timeout:
            if GPIO.input(sensors.get("open")):
                return time.time() - start
            time.sleep(0.1)

        return None

    def maal_lukketid(self, port, timeout=60):
        """Måler tid fra port starter lukking til lukket-sensor er aktiv."""
        sensors = self.sensor_pins.get(port)
        if not sensors:
            return None

        status = self.get_port_status(port)
        if status == "lukket":
            log_event("info", f"{port} er allerede lukket")
            return None

        self.open_port(port)
        start = time.time()

        while time.time() - start < timeout:
            if GPIO.input(sensors.get("closed")):
                return time.time() - start
            time.sleep(0.1)

        return None
