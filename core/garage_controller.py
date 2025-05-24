import time
import threading

from utils.relay_control import RelayControl
from utils.garage_logger import GarageLogger
from utils.config_loader import load_config, load_portlogic_config


# Forsøk å importere pigpio-monitor, fallback til None hvis ikke tilgjengelig
try:
    from utils.sensor_monitor import SensorMonitor
except ImportError:
    SensorMonitor = None


class GarageController:
    def __init__(self, config_gpio, config_system, testing_mode=False):
        self.config_portlogic = load_portlogic_config()
        self.config_gpio = config_gpio
        self.config_system = config_system
        self.testing_mode = testing_mode

        self.logger = GarageLogger()
        self.relay_control = RelayControl(config_gpio)
        self.status = {}  # f.eks. {'port1': 'closed'}
        self._operation_flags = {}  # f.eks. {'port1': {'moving': True, 'start_time': 123456}}


        # Last tidligere målte åpne-/lukketider
        self.timing_data = config_system.get("timing", {})

        self.sensor_monitor = None
        if not testing_mode and SensorMonitor:
            self.sensor_monitor = SensorMonitor(
                self.config_gpio["sensor_pins"],
                self.sensor_event_callback
            )

        self._init_port_statuses()

    def _init_port_statuses(self):
        for port in self.config_gpio["sensor_pins"]:
            self.status[port] = "unknown"
            self._operation_flags[port] = {"moving": False, "start_time": None}

    def sensor_event_callback(self, port, sensor_type, level):
        active_state = self.config_gpio["sensor_config"]["active_state"]
        is_active = (level == active_state)

        self.logger.log_status_change(port, f"{sensor_type} sensor {'aktiv' if is_active else 'inaktiv'}")

        if is_active:
            new_status = "open" if sensor_type == "open" else "closed"
            self.status[port] = new_status

            if self._operation_flags[port]["moving"]:
                # Fullfør tidsmåling
                elapsed = time.time() - self._operation_flags[port]["start_time"]
                direction = "open" if sensor_type == "open" else "close"
                self.logger.log_timing(port, direction, elapsed)

                self._operation_flags[port]["moving"] = False
                self._operation_flags[port]["start_time"] = None
        else:
            self.status[port] = "moving"

    def open_port(self, port):
        if self.status.get(port) == "open":
            return {"port": port, "status": "already open"}

        self.logger.log_action(port, "open", source="api")
        self.relay_control.trigger(port)
        self._operation_flags[port]["moving"] = True
        self._operation_flags[port]["start_time"] = time.time()

        if self.testing_mode:
            self.sensor_event_callback(port, "open", 0)

        return {"port": port, "action": "open initiated"}

    def close_port(self, port):
        if self.status.get(port) == "closed":
            return {"port": port, "status": "already closed"}

        self.logger.log_action(port, "close", source="api")
        self.relay_control.trigger(port)
        self._operation_flags[port]["moving"] = True
        self._operation_flags[port]["start_time"] = time.time()

        if self.testing_mode:
            self.sensor_event_callback(port, "closed", 0)

        return {"port": port, "action": "close initiated"}

    def stop_port(self, port):
        if not self._operation_flags[port]["moving"]:
            return {"port": port, "status": "not moving"}

        self._operation_flags[port]["moving"] = False
        self.logger.log_action(port, "stop", source="api")
        return {"port": port, "status": "stopped"}

    def get_current_status(self, port):
        return self.status.get(port, "unknown")

    def get_all_statuses(self):
        return self.status
    
    def get_port_names(self):
        return list(self.relay_control.relay_pins.keys())

    def get_reported_status(self, port):
        """
        Returnerer vurdert status for porten.
        Bruker sensorstatus og eventuell bevegelsesstatus.
        """
        if self._operation_flags[port]["moving"]:
            return "moving"

        status = self.status.get(port, "unknown")
        return status

    def _update_timing_data(self, port, direction, duration):
        data = self.config_system.setdefault("timing", {}).setdefault(port, {}).setdefault(direction, {})
        history = data.get("history", [])
        history.append(round(duration, 2))

        max_len = self.config_portlogic["timing_history_length"]
        if len(history) > max_len:
            history = history[-max_len:]

        avg = round(sum(history) / len(history), 2)
        last = round(duration, 2)

        self.config_system["timing"][port][direction] = {
            "last": last,
            "avg": avg,
            "history": history
        }

        self._write_config_to_disk()

    def _write_config_to_disk(self):
        with open(paths.CONFIG_SYSTEM_PATH, "w") as f:
            json.dump(self.config_system, f, indent=2)

    def _handle_relay_timeout(self, port):
        flags = self._operation_flags.get(port, {})
        if flags.get("first_sensor_time") is None:
            self._set_status(port, self.status.get(port))  # behold forrige status
            self.logger.log_status(port, "Ingen sensorrespons – motor trolig ikke aktivert")
            self.logger.log_error(port, "Puls sendt, men ingen sensor endret status")
            flags["moving"] = False

    def _handle_movement_timeout(self, port):
        flags = self._operation_flags.get(port, {})
        if flags.get("moving"):
            source = "system" if flags.get("stopped_by_system") else "manuell"
            self._set_status(port, "partial")
            self.logger.log_status(port, f"Port stoppet – delvis åpen (kilde: {source})")
            self.logger.log_error(port, f"{port} | bevegelse ikke fullført innen forventet tid | kilde: {source}")
            flags["moving"] = False


    def cleanup(self):
        if self.sensor_monitor:
            self.sensor_monitor.stop()
        self.relay_control.cleanup()
