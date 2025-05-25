import datetime
import time, json, threading 
import pigpio
from datetime import datetime

from config import config_paths as paths
from utils.relay_control import RelayControl
from utils.garage_logger import GarageLogger
from utils.config_loader import load_config, load_portlogic_config
from utils.gpio_initializer import configure_gpio_pins
from utils.pigpio_manager import get_pi





# Forsøk å importere pigpio-monitor, fallback til None hvis ikke tilgjengelig
try:
    from utils.sensor_monitor import SensorMonitor
except ImportError:
    SensorMonitor = None


class GarageController:
    def __init__(self, config_gpio, config_system, testing_mode=False):
        self.pi = get_pi()
        self.config_gpio = config_gpio
        self.config_system = config_system
        self.testing_mode = testing_mode
        self.relay_control = RelayControl(config_gpio, logger=self.logger, pi=self.pi)
        self.sensor_monitor = SensorMonitor(config_gpio, logger=self.logger, pi=self.pi)


        self.logger = GarageLogger(paths.STATUS_LOG, paths.ERROR_LOG)
        self.relay_control = RelayControl(config_gpio, self.logger)

        self.timing_enabled = not self.testing_mode

        # SensorMonitor må initieres før portstatus kan leses
        self.sensor_monitor = SensorMonitor(config_gpio, self.logger)
        self.sensor_monitor.set_callback(self._sensor_callback)
        self.logger.log_status("init", "SensorMonitor aktivert og callback satt")

        # Kombinert initiering av status og GPIO-avlesning
        self._initialize_port_states()
        # Konfigurer GPIO med riktig pull-oppsett
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("Kunne ikke koble til pigpiod")
        sensor_pins = config_gpio.get("sensor_pins", {})
        pull = config_gpio.get("sensor_config", {}).get("pull", "off")
        configure_gpio_pins(sensor_pins, pull, self.pi)

    def _initialize_port_states(self):
        """
        Oppretter portstatus og flags + leser sanntidsstatus fra GPIO
        """
        self.status = {}
        self._operation_flags = {}

        for port, pins in self.config_gpio["sensor_pins"].items():
            self.status[port] = "unknown"
            self._operation_flags[port] = {"moving": False, "start_time": None}

            try:
                open_pin = pins.get("open")
                closed_pin = pins.get("closed")

                open_active = self.sensor_monitor.pi.read(open_pin) == 1
                closed_active = self.sensor_monitor.pi.read(closed_pin) == 1

                if open_active and not closed_active:
                    self.status[port] = "open"
                elif closed_active and not open_active:
                    self.status[port] = "closed"
                elif open_active and closed_active:
                    self.status[port] = "error"  # Fysisk feil
                else:
                    self.status[port] = "partial"  # Ingen aktiv sensor

                self.logger.log_status("controller", f"Init status port {port}: {self.status[port]}")
            except Exception as e:
                self.logger.log_warning("controller", f"Kunne ikke lese initial status for port {port}: {e}")
                self.status[port] = "unknown"

    # (Resten av GarageController beholdes uendret)
    # Du har open_port, close_port, stop_port, _sensor_callback, _store_timing, osv.

    def save_config(self):
        """Skriver oppdatert systemkonfig til fil"""
        try:
            with open(paths.CONFIG_SYSTEM_PATH, "w") as f:
                json.dump(self.config_system, f, indent=4)
        except Exception as e:
            self.logger.log_error("controller", f"Kunne ikke lagre systemkonfig: {e}")

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
                self.status[port] = direction  # "open" eller "closed"
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
        """
        Oppdaterer sist målte og gjennomsnittlig åpne-/lukketid for porten.
        """
        direction_key = f"{direction}_time"
        last_key = f"last_{direction_key}"
        avg_key = f"avg_{direction_key}"
        list_key = f"history_{direction_key}"

        # Fallbackverdi dersom historikk ikke finnes
        default_time = self.config_system.get(f"default_{direction_key}", 10.0)
        history_size = self.config_gpio.get("timing_config", {}).get("timing_history_size", 3)

        if port not in self.config_system:
            self.config_system[port] = {}

        port_data = self.config_system[port]

        # Lagre siste måling
        port_data[last_key] = round(duration, 2)

        # Bygg og oppdater historikk
        history = port_data.get(list_key, [])
        history.append(round(duration, 2))
        if len(history) > history_size:
            history.pop(0)

        port_data[list_key] = history

        # Beregn snitt
        if history:
            avg = round(sum(history) / len(history), 2)
        else:
            avg = default_time

        port_data[avg_key] = avg

        # Lagre til config_system.json
        try:
            with open(paths.CONFIG_SYSTEM_PATH, "w") as f:
                json.dump(self.config_system, f, indent=2)
            self.logger.log_status("timing", f"{port} {direction}: tid={duration:.2f}s, snitt={avg:.2f}s")
        except Exception as e:
            self.logger.log_error("timing", f"Feil ved lagring av timingdata: {e}")


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

    def _sensor_callback(self, gpio, level, tick, port, sensor_type):
        """
        Callback-funksjon som trigges når en sensor endrer tilstand.
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logger.log_status("sensor", f"{port} {sensor_type} sensor endret: level={level} @ {timestamp}")

        if port not in self.status:
            self.logger.log_error("sensor", f"Ukjent port i callback: {port}")
            return

        direction = self._operation_flags[port].get("direction")
        start_time = self._operation_flags[port].get("start_time")
        moving = self._operation_flags[port].get("moving", False)

        now = time.time()

        expected_sensor = "open" if direction == "open" else "closed"
        opposite_sensor = "closed" if direction == "open" else "open"

        # Hvis riktig sensor trigges under bevegelse
        if moving and sensor_type == expected_sensor and start_time:
            elapsed = now - start_time
            self.logger.log_timing(port, {
                "direction": direction,
                "duration": round(elapsed, 2),
                "timestamp": timestamp
            })
            self._update_timing_data(port, direction, elapsed)
            self.status[port] = direction
            self.logger.log_status("status", f"{port} er nå {direction}")
            self._operation_flags[port].update({
                "moving": False,
                "start_time": None,
                "direction": None
            })

        # Hvis motsatt sensor trigges under bevegelse
        elif moving and sensor_type == opposite_sensor:
            self.logger.log_warning("sensor", f"{port}: Motsatt sensor ({sensor_type}) aktivert under {direction}-bevegelse – mulig manuell stopp eller feil")
            self.status[port] = "partial"
            self._operation_flags[port].update({
                "moving": False,
                "start_time": None,
                "direction": None
            })

        # Uansett – oppdater status basert på sensorene
        open_active = self.sensor_monitor.is_sensor_active(port, "open")
        closed_active = self.sensor_monitor.is_sensor_active(port, "closed")

        if open_active and not closed_active:
            new_status = "open"
        elif closed_active and not open_active:
            new_status = "closed"
        elif not open_active and not closed_active:
            new_status = "partial"
        elif open_active and closed_active:
            new_status = "sensor_error"
        else:
            new_status = self.status.get(port, "unknown")

        if self.status.get(port) != new_status:
            self.status[port] = new_status
            self.logger.log_status("status", f"{port} sensorbasert status = {new_status}")

        # Skriv status til config_system.json
        try:
            with open(paths.CONFIG_SYSTEM_PATH, "w") as f:
                json.dump(self.config_system, f, indent=2)
        except Exception as e:
            self.logger.log_error("config", f"Feil ved lagring av config_system.json: {e}")


    def shutdown(self):
        """
        Rydderessurser ved avslutning av systemet.
        """
        from utils.pigpio_manager import stop_pi
        stop_pi()

        if hasattr(self, "sensor_monitor"):
            self.sensor_monitor.stop()
        if hasattr(self, "relay_control"):
            self.relay_control.cleanup()
        self.logger.log_status("system", "GarageController avsluttet og ryddet opp.")
