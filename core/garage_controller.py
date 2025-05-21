import time
import json
import threading
import pigpio
from utils.garage_logger import log_action, log_status, log_error
from utils.file_utils import read_config

class GarageController:
    def __init__(self):
        self.config_gpio = read_config("config/config_gpio.json")
        self.relay_pins = self.config_gpio["relay_pins"]
        self.sensor_pins = self.config_gpio["sensor_pins"]
        self.relay_config = self.config_gpio["relay_config"]
        self.sensor_config = self.config_gpio["sensor_config"]

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("pigpiod er ikke aktivt. Start med sudo pigpiod")

        self.sensor_callbacks = {}
        self.sensor_states = {}  # f.eks. {'port1': {'open': 0, 'closed': 1}}

        self._setup_gpio()
        self._init_sensor_states()

    def _setup_gpio(self):
        # Rele-pinner
        for pin in self.relay_pins.values():
            self.pi.set_mode(pin, pigpio.OUTPUT)
            self.pi.write(pin, 1 - self.relay_config["active_state"])  # inaktiv

        # Sensor-pinner
        for port, pins in self.sensor_pins.items():
            for state, pin in pins.items():
                self.pi.set_mode(pin, pigpio.INPUT)
                self.pi.set_pull_up_down(pin, pigpio.PUD_UP)
                self.pi.set_glitch_filter(pin, 3000)  # debounce 3ms
                cb = self.pi.callback(pin, pigpio.EITHER_EDGE, self._sensor_callback)
                self.sensor_callbacks[pin] = cb

    def _init_sensor_states(self):
        for port, pins in self.sensor_pins.items():
            self.sensor_states[port] = {}
            for state, pin in pins.items():
                level = self.pi.read(pin)
                self.sensor_states[port][state] = level

    def _sensor_callback(self, gpio, level, tick):
        # Finn port og sensor-type (open/closed)
        for port, pins in self.sensor_pins.items():
            for state, pin in pins.items():
                if pin == gpio:
                    self.sensor_states[port][state] = level
                    status_str = "AKTIV" if level == self.sensor_config["active_state"] else "INAKTIV"
                    print(f"[{port}] Sensor '{state}' → {status_str}")
                    log_status(port, f"sensor_{state} = {status_str}")
                    break

    def get_current_status(self, port):
        open_pin = self.sensor_pins[port]["open"]
        closed_pin = self.sensor_pins[port]["closed"]
        active = self.sensor_config["active_state"]

        open_active = self.pi.read(open_pin) == active
        closed_active = self.pi.read(closed_pin) == active

        if open_active and not closed_active:
            return "open"
        elif not open_active and closed_active:
            return "closed"
        elif not open_active and not closed_active:
            return "moving"
        elif open_active and closed_active:
            return "sensor_error"
        else:
            return "unknown"

    def pulse_relay(self, port):
        pin = self.relay_pins[port]
        active = self.relay_config["active_state"]
        duration = self.relay_config["pulse_duration"]

        print(f"[{port}] Puls på GPIO {pin} i {duration} sek")
        log_action(port, "pulse", "api")

        self.pi.write(pin, active)
        time.sleep(duration)
        self.pi.write(pin, 1 - active)

    def activate_port(self, port, direction):
        # Avhengig av open/close-knapp
        current = self.get_current_status(port)
        if direction == "open" and current == "open":
            return "Allerede åpen"
        if direction == "close" and current == "closed":
            return "Allerede lukket"

        log_action(port, direction, "api")
        self.pulse_relay(port)
        return f"Starter {direction}..."

    def stop_port(self, port):
        if self.get_current_status(port) == "moving":
            log_action(port, "stop", "api")
            self.pulse_relay(port)
            return "Port stoppet"
        return "Port er ikke i bevegelse"

    def cleanup(self):
        print("Opprydding av GPIO og callbacks")
        for cb in self.sensor_callbacks.values():
            cb.cancel()
        self.pi.stop()
