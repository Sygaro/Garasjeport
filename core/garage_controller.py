# ==========================================
# Filnavn: garage_controller.py
# Polling-basert versjon med konfigbart intervall
# ==========================================

import lgpio
import time
import threading
import json
from core.garage_logger import GarageLogger
import os


class GarageController:
    def __init__(self, config_path='config.json'):
        self.logger = GarageLogger()
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self.chip = lgpio.gpiochip_open(0)

        self.relay_pins = {}
        self.sensor_pins = {}
        self.sensor_states = {}
        self.port_status = {'port1': 'unknown', 'port2': 'unknown'}
        self.motion_start_time = {}

        self.polling_interval_ms = self.config.get('polling_interval_ms', 100)

        self._setup_gpio()
        self._start_polling_thread()

    def _load_config(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def _setup_gpio(self):
        for port in ['port1', 'port2']:
            relay_pin = self.config['relay_pins'][port]
            lgpio.gpio_claim_output(self.chip, relay_pin)
            self.relay_pins[port] = relay_pin

            for state in ['open', 'closed']:
                pin = self.config['sensor_pins'][port][state]
                lgpio.gpio_claim_input(self.chip, pin, lgpio.SET_PULL_UP)
                self.sensor_pins[(port, state)] = pin
                self.sensor_states[(port, state)] = self._read_pin(pin)

    def _start_polling_thread(self):
        thread = threading.Thread(target=self._polling_loop, daemon=True)
        thread.start()

    def _polling_loop(self):
        while True:
            for (port, state), pin in self.sensor_pins.items():
                current = self._read_pin(pin)
                previous = self.sensor_states[(port, state)]

                if current != previous:
                    self.sensor_states[(port, state)] = current
                    self._handle_sensor_change(port)

            time.sleep(self.polling_interval_ms / 1000.0)

    def _read_pin(self, pin):
        return lgpio.gpio_read(self.chip, pin) == 0  # aktiv lav

    def _handle_sensor_change(self, port):
        new_status = self._determine_status(port)
        if new_status != self.port_status[port]:
            self.port_status[port] = new_status
            self.logger.log_status_change(port, new_status)

    def _determine_status(self, port):
        sensor_open = self.sensor_states[(port, 'open')]
        sensor_closed = self.sensor_states[(port, 'closed')]

        if sensor_open and not sensor_closed:
            return 'open'
        elif not sensor_open and sensor_closed:
            return 'closed'
        elif not sensor_open and not sensor_closed:
            elapsed = time.time() - self.motion_start_time.get(port, 0)
            max_time = self.config['calibration'][port]['open_time']
            if elapsed > max_time + 2:
                return 'partial_open'
            return 'moving'
        elif sensor_open and sensor_closed:
            return 'sensor_error'
        return 'unknown'

    def activate_motor_relay(self, port, source='api'):
        if self.port_status[port] == 'sensor_error':
            self.logger.log_action(port, 'blocked', source, 'sensor_error')
            return False

        self.motion_start_time[port] = time.time()
        relay_pin = self.relay_pins[port]

        lgpio.gpio_write(self.chip, relay_pin, 1)
        time.sleep(0.3)
        lgpio.gpio_write(self.chip, relay_pin, 0)

        self.logger.log_action(port, 'pulse_sent', source)
        return True

    def get_current_status(self, port):
        return self.port_status[port]

    def reload_config(self):
        """Laster inn config.json og oppdaterer interne verdier."""
        self.config = self._load_config(self.config_path)
        self.polling_interval_ms = self.config.get("polling_interval_ms", 1000)
        # Du kan også reinitialisere relepinner/sensorer her hvis ønskelig


    def cleanup(self):
        for pin in self.relay_pins.values():
            lgpio.gpio_free(self.chip, pin)
        for pin in self.sensor_pins.values():
            lgpio.gpio_free(self.chip, pin)
        lgpio.gpiochip_close(self.chip)
