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
import threading
import RPi.GPIO as GPIO
from event_log import log_event

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

    # Måler tiden det tar å åpne/lukke portene
    def maal_aapnetid(self, port, timeout=30):
        relay_pin = self.config["relay_pins"].get(port)
        sensor_pins = self.config["sensor_pins"].get(port, {})
        open_sensor = sensor_pins.get("open")
        closed_sensor = sensor_pins.get("closed")
        if not all([relay_pin, open_sensor, closed_sensor]):
            log_event("error", "Mangler GPIO-konfig for port", port=port)
            return None
        status_closed = GPIO.input(closed_sensor)
        status_open = GPIO.input(open_sensor)
        if status_open == GPIO.HIGH:
            log_event("info", "Port allerede åpen – ingen måling", port=port)
            return 0.0
        log_event("calibration", "Starter automatisk måling", port=port)
        maaling = {"start": None, "slutt": None}

        def closed_faller(channel):
            maaling["start"] = time.perf_counter()
            log_event("sensor", "Lukket sensor inaktiv – start måling", port=port)

        def open_stiger(channel):
            maaling["slutt"] = time.perf_counter()
            log_event("sensor", "Åpen sensor aktiv – stopp måling", port=port)

        # Sett opp sensorhendelser
        GPIO.add_event_detect(closed_sensor, GPIO.FALLING, callback=closed_faller, bouncetime=200)
        GPIO.add_event_detect(open_sensor, GPIO.RISING, callback=open_stiger, bouncetime=200)
        # Aktiver port (simuler knappetrykk)
        GPIO.output(relay_pin, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(relay_pin, GPIO.LOW)
        # Vent i separat tråd på slutt eller timeout
        start_tid = time.time()
        while time.time() - start_tid < timeout:
            if maaling["start"] and maaling["slutt"]:
                break
            time.sleep(0.1)
        GPIO.remove_event_detect(closed_sensor)
        GPIO.remove_event_detect(open_sensor)
        if not (maaling["start"] and maaling["slutt"]):
            log_event("error", "Kalibrering feilet – ingen fullføring", port=port, data={"timeout": timeout})
            return None
        varighet = round(maaling["slutt"] - maaling["start"], 2)
        log_event("calibration", "Målt åpnetid fullført", port=port, data={"sekunder": varighet})
        return varighet
