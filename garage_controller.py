
# Fil: garage_controller.py (gpiod-versjon) 
# Erstattet RPi.GPIO med gpiod v2

import time
import gpiod
import threading
from event_log import log_event

def sensor_callback(channel, socketio=None):
    for port, sensors in garage.sensor_pins.items():
        for position, pin in sensors.items():
            if pin == channel:
                status = garage.get_port_status(port)
                if socketio:
                    socketio.emit("status_update", {
                        "port": port,
                        "status": status
                    })
                return


class GarageController:
    def __init__(self, config):
        from garage_controller import sensor_callback

        self.config = config
        self.relay_pins = config.get("relay_pins", {})
        self.sensor_pins = config.get("sensor_pins", {})

        self.chip = gpiod.Chip("gpiochip0")
        self.relay_lines = {}  # {bcm: line}
        self.sensor_lines = {}  # {bcm: line}
        self.sensor_threads = []
        self.stop_event = threading.Event()

        # Sett opp releer (output)
        for pin in self.relay_pins.values():
            line = self.chip.get_line(pin)
            line.request(consumer="garage", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[1])
            self.relay_lines[pin] = line

        # Sett opp sensorer (input + pull-up + edge detection)
        for port, sensors in self.sensor_pins.items():
            for position, pin in sensors.items():
                line = self.chip.get_line(pin)
                line.request(consumer="garage", type=gpiod.LINE_REQ_EV_BOTH_EDGES, flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)
                self.sensor_lines[pin] = line
                thread = threading.Thread(target=self._monitor_sensor_line, args=(line, sensor_callback), daemon=True)
                thread.start()
                self.sensor_threads.append(thread)

        print("✔️ gpiod: Alle rele og sensor-GPIOer konfigurert.")

    def _monitor_sensor_line(self, line, callback):
        while not self.stop_event.is_set():
            if line.event_wait(1):
                event = line.event_read()
                callback(line.offset())

    def legg_til_event(self, pin, callback):
        pass  # Ikke nødvendig lenger – håndteres automatisk

    def cleanup(self):
        self.stop_event.set()
        for line in self.relay_lines.values():
            line.set_value(1)
            line.release()
        for line in self.sensor_lines.values():
            line.release()
        self.chip.close()

    def update_config(self, new_config):
        self.cleanup()
        self.__init__(new_config)

    def open_port(self, port):
        pin = self.relay_pins.get(port)
        if pin is None:
            log_event("error", f"Ugyldig portnavn: {port}")
            return False
        line = self.relay_lines[pin]
        log_event("action", f"Sender åpen/lukk-impuls til {port}", data={"gpio": pin})
        line.set_value(0)
        time.sleep(self.config.get("relay_pulse_length", 0.5))
        line.set_value(1)
        return True

    def get_port_status(self, port):
        pins = self.sensor_pins.get(port)
        if not pins:
            return "ukjent"
        open_state = self.sensor_lines[pins.get("open")].get_value()
        closed_state = self.sensor_lines[pins.get("closed")].get_value()

        if open_state == 0 and closed_state == 1:
            return "åpen"
        elif open_state == 1 and closed_state == 0:
            return "lukket"
        elif open_state == 1 and closed_state == 1:
            return "ukjent"
        elif open_state == 0 and closed_state == 0:
            return "sensorfeil"
        else:
            return "ukjent"

    def maal_aapnetid(self, port, timeout=60):
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
            if self.sensor_lines[sensors.get("open")].get_value():
                return time.time() - start
            time.sleep(0.1)
        return None

    def maal_lukketid(self, port, timeout=60):
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
            if self.sensor_lines[sensors.get("closed")].get_value():
                return time.time() - start
            time.sleep(0.1)
        return None

    def send_pulse(self, port):
        pin = self.relay_pins.get(port)
        if pin is None:
            raise ValueError(f"Ukjent port: {port}")
        line = self.relay_lines[pin]
        line.set_value(0)
        time.sleep(0.3)
        line.set_value(1)

    def read_sensor(self, port, position):
        pin = self.sensor_pins.get(port, {}).get(position)
        if pin is None:
            raise ValueError(f"Sensor '{position}' mangler for port: {port}")
        return self.sensor_lines[pin].get_value()

    def try_send_pulse(self, port, action="open"):
        status = self.get_port_status(port)
        if action == "open":
            if status == "åpen":
                return False, "Porten er allerede åpen"
            elif status == "sensorfeil":
                return False, "Sensorfeil – portstatus kan ikke bekreftes"
            elif status == "ukjent":
                return False, "ukjent"
        elif action == "close":
            if status == "lukket":
                return False, "Porten er allerede lukket"
            elif status == "sensorfeil":
                return False, "Sensorfeil – portstatus kan ikke bekreftes"
            elif status == "ukjent":
                return False, "ukjent"

        pin = self.relay_pins.get(port)
        if pin is None:
            return False, f"Port {port} finnes ikke"
        line = self.relay_lines[pin]
        line.set_value(0)
        time.sleep(0.3)
        line.set_value(1)
        return True, f"Signal sendt – porten forsøkes {action}et"

    def send_pulse_raw(self, port):
        pin = self.relay_pins.get(port)
        if pin is None:
            raise ValueError(f"Port {port} finnes ikke")
        line = self.relay_lines[pin]
        line.set_value(0)
        time.sleep(0.3)
        line.set_value(1)


