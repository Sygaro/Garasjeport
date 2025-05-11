import RPi.GPIO as GPIO
import time
import logging
from event_log import log_event

logger = logging.getLogger(__name__)

class GarageController:
    def __init__(self, config):
        self.config = config
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for port, relay_pin in self.config.get("relay_pins", {}).items():
            GPIO.setup(relay_pin, GPIO.OUT, initial=GPIO.HIGH)

        for port, sensors in self.config.get("sensor_pins", {}).items():
            for state, pin in sensors.items():
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def cleanup(self):
        GPIO.cleanup()

    def open_port(self, port):
        try:
            relay_pin = self.config["relay_pins"][port]
            pulse_time = 0.5

            logger.info(f"🔌 Åpner port {port} via rele {relay_pin}")
            log_event("action", "Åpner port", port=port, data={"pin": relay_pin})
            GPIO.output(relay_pin, GPIO.LOW)
            time.sleep(pulse_time)
            GPIO.output(relay_pin, GPIO.HIGH)
            return True
        except Exception as e:
            logger.error(f"❌ Feil ved åpning av port {port}: {e}")
            log_event("error", "Feil ved åpning av port", port=port, data={"feil": str(e)})
            return False

    def get_status(self, port):
        try:
            sensors = self.config["sensor_pins"].get(port)
            if not sensors:
                return "ukjent"

            open_pin = sensors.get("open")
            closed_pin = sensors.get("closed")

            is_open = not GPIO.input(open_pin)
            is_closed = not GPIO.input(closed_pin)

            if is_open and not is_closed:
                return "åpen"
            elif is_closed and not is_open:
                return "lukket"
            elif not is_open and not is_closed:
                return "midtposisjon"
            else:
                return "ukjent"
        except Exception as e:
            logger.warning(f"Feil ved statuslesing av port {port}: {e}")
            return "feil"

    def maal_aapnetid(self, port):
        sensors = self.config.get("sensor_pins", {}).get(port)
        if not sensors:
            return None

        open_pin = sensors.get("open")
        self.open_port(port)
        start = time.time()
        timeout = 30
        while time.time() - start < timeout:
            if not GPIO.input(open_pin):
                varighet = round(time.time() - start, 2)
                log_event("calibration", "Åpnetid målt", port=port, data={"sekunder": varighet})
                return varighet
            time.sleep(0.1)
        return None

    def maal_lukketid(self, port):
        sensors = self.config.get("sensor_pins", {}).get(port)
        if not sensors:
            return None

        closed_pin = sensors.get("closed")
        self.open_port(port)
        start = time.time()
        timeout = 30
        while time.time() - start < timeout:
            if not GPIO.input(closed_pin):
                varighet = round(time.time() - start, 2)
                log_event("calibration", "Lukketid målt", port=port, data={"sekunder": varighet})
                return varighet
            time.sleep(0.1)
        return None


import time
from event_log import log_event

def calibrate_port(port, timeout=30):
    start_time = time.time()
    # Start kalibrering, vent til port er åpen
    while not is_open(port):
        if time.time() - start_time > timeout:
            log_event("error", "Kalibrering feilet – ingen fullføring", port=port, data={"timeout": timeout})
            return None
        time.sleep(0.1)
    open_time = time.time() - start_time

    # Lukker porten og måler lukketid
    close_port(port)
    start_close_time = time.time()
    while not is_closed(port):
        if time.time() - start_close_time > timeout:
            log_event("error", "Kalibrering lukketid feilet – ingen fullføring", port=port, data={"timeout": timeout})
            return None
        time.sleep(0.1)
    close_time = time.time() - start_close_time

    return {"open_time": open_time, "close_time": close_time}
