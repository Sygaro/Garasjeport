import time
import lgpio
import threading
from logger import GarageLogger
from configparser import ConfigParser
import json


class GPIOManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GPIOManager, cls).__new__(cls)
            cls._instance.chip = lgpio.gpiochip_open(0)
            cls._instance.claimed_pins = set()
        return cls._instance

    def claim_output(self, pin):
        if pin not in self.claimed_pins:
            lgpio.gpio_claim_output(self.chip, pin)
            self.claimed_pins.add(pin)

    def claim_input(self, pin):
        if pin not in self.claimed_pins:
            lgpio.gpio_claim_input(self.chip, pin, lgpio.SET_PULL_UP)
            self.claimed_pins.add(pin)

    def write(self, pin, value):
        lgpio.gpio_write(self.chip, pin, value)

    def read(self, pin):
        return lgpio.gpio_read(self.chip, pin)

    def set_alert(self, pin, callback):
        lgpio.gpio_set_alert_func(self.chip, pin, callback)

    def cleanup(self):
        for pin in self.claimed_pins:
            lgpio.gpio_free(self.chip, pin)
        lgpio.gpiochip_close(self.chip)


class GarageController:
    def __init__(self, config_path='config.json'):
        self.gpio = GPIOManager()
        self.logger = GarageLogger()
        self.config = self._load_config(config_path)
        self.status = {'port1': 'unknown', 'port2': 'unknown'}
        self.motion_timer = {}
        self.motion_start_time = {}
        self._setup_gpio()

    def _load_config(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def _setup_gpio(self):
        for port in ['port1', 'port2']:
            self.gpio.claim_output(self.config['relay_pins'][port])
            for state in ['open', 'closed']:
                sensor_pin = self.config['sensor_pins'][port][state]
                self.gpio.claim_input(sensor_pin)
                self.gpio.set_alert(sensor_pin, self._make_alert_callback(port))

    def _make_alert_callback(self, port):
        def callback(chip, pin, level, tick):
            self._update_port_status(port)
        return callback

    def _update_port_status(self, port):
        sensor_open = self._read_sensor(port, 'open')
        sensor_closed = self._read_sensor(port, 'closed')

        if sensor_open and not sensor_closed:
            new_status = 'open'
        elif not sensor_open and sensor_closed:
            new_status = 'closed'
        elif not sensor_open and not sensor_closed:
            new_status = 'moving'
            # Sjekk for timeout
            if port in self.motion_start_time:
                duration = time.time() - self.motion_start_time[port]
                expected = self._get_max_motion_time(port)
                if duration > expected + 2:
                    new_status = 'partial_open'
        elif sensor_open and sensor_closed:
            new_status = 'sensor_error'
        else:
            new_status = 'unknown'

        if new_status != self.status[port]:
            self.status[port] = new_status
            self.logger.log_status_change(port, new_status)

    def _read_sensor(self, port, state):
        pin = self.config['sensor_pins'][port][state]
        return self.gpio.read(pin) == 0  # Aktiv lav

    def _get_max_motion_time(self, port):
        return self.config['calibration'][port]['open_time']  # Bruk åpne som referanse

    def activate_motor_relay(self, port, source='app'):
        current_status = self.status[port]
        if current_status == 'sensor_error':
            self.logger.log_action(port, 'blocked', source, 'sensor_error')
            return False

        self.motion_start_time[port] = time.time()

        relay_pin = self.config['relay_pins'][port]
        self.gpio.write(relay_pin, 1)
        time.sleep(0.3)
        self.gpio.write(relay_pin, 0)

        self.logger.log_action(port, 'pulse_sent', source)
        return True

    def get_current_status(self, port):
        self._update_port_status(port)
        return self.status[port]

    def cleanup(self):
        self.gpio.cleanup()
