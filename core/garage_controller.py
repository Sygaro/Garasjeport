import datetime
import time, json #, threading 

#import pigpio
from datetime import datetime

from config import config_paths as paths
from utils.relay_control import trigger
from utils.logging.unified_logger import get_logger
# from utils.config_loader import load_config, load_portlogic_config
# from utils.gpio_initializer import configure_gpio_pins
from utils.pigpio_manager import get_pi, stop_pi
from monitor.port_sensor_monitor import SensorMonitor



# Forsøk å importere pigpio-monitor, fallback til None hvis ikke tilgjengelig
try:
    from monitor.port_sensor_monitor import SensorMonitor
except ImportError:
    SensorMonitor = None


class GarageController:
    def __init__(self, config_gpio, config_system, relay_pins, relay_config, testing_mode=False):
       
        ### Setter opp logging ###
        # Logger instanser for ulike kategorier
      
        self.activity_logger = get_logger(name="GarageController", category="port_activity", source="API")
        self.status_logger = get_logger("GarageController", category="port_status")
        self.timing_logger = get_logger("GarageController", category="port_timing")
        self.logger = get_logger("GarageController", category="garage_controller")

        self.logger.info("GarageController startet")
       
        self.config_gpio = config_gpio
        self.config_system = config_system
        self.relay_pins = relay_pins
        self.relay_config = relay_config
        self.testing_mode = testing_mode
        self.status = {}
        self._operation_flags = {}

        # Hent pigpio-instans via delt manager
        self.pi = get_pi()
        if self.pi is None or not self.pi.connected:
            self.logger.error("pigpio er ikke tilgjengelig – sjekk tilkoblingen.")
            raise RuntimeError("Feil: pigpio er ikke tilgjengelig")
                

        self.sensor_monitor = SensorMonitor(
            config_gpio=config_gpio,
            pi=self.pi
        )
        if hasattr(self.sensor_monitor, "set_callback"):
            self.sensor_monitor.set_callback(self.sensor_event_callback)

        self._initialize_port_states()



    def _initialize_port_states(self):
        """
        Oppretter portstatus og flags + leser sanntidsstatus fra GPIO
        """
        self.status = {}
        self._operation_flags = {}

        for port, pins in self.config_gpio["sensor_pins"].items():
            self.status[port] = "unknown"
            self._operation_flags[port] = {"moving": False, "start_time": None, "direction": None}

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
                    self.status[port] = "sensor_error"  # Sensorfeil
                elif not open_active and not closed_active:
                    self.status[port] = "partial"  # Ingen aktiv sensor
                else:
                    self.status[port] = "unknown"

                self.status_logger.info(f"Init status port {port}: {self.status[port]}")
                self.status_logger.info(f"{port} sensorstatus ved oppstart: {self.status[port]}")

            except Exception as e:
                self.logger.warning(f"Kunne ikke lese initial status for port {port}: {e}")
                self.status[port] = "unknown"





    def save_config(self):
        """Skriver oppdatert systemkonfig til fil"""
        try:
            with open(paths.CONFIG_SYSTEM_PATH, "w") as f:
                json.dump(self.config_system, f, indent=4)
        except Exception as e:
            self.logger.error(f"Kunne ikke lagre systemkonfig: {e}")

    def sensor_event_callback(self, port, sensor_type, level):
        active_state = self.config_gpio["sensor_config"]["active_state"]
        is_active = (level == active_state)

        self.status_logger.change(f"{port}: {sensor_type} sensor {'aktiv' if is_active else 'inaktiv'}")

        if is_active:
            new_status = "open" if sensor_type == "open" else "closed"
            self.status[port] = new_status

            if self._operation_flags[port]["moving"]:
                # Fullfør tidsmåling
                elapsed = time.time() - self._operation_flags[port]["start_time"]
                direction = "open" if sensor_type == "open" else "close"
                self.status[port] = direction  # "open" eller "closed"
                self.timing_logger.timing(port, direction, elapsed)

                self._operation_flags[port]["moving"] = False
                self._operation_flags[port]["start_time"] = None
        else:
            self.status[port] = "moving"
            
    def open_port(self, port):
        if self.status.get(port) == "open":
            return {"port": port, "status": "already open"}

        print([m for m in dir(logger) if not m.startswith("_")])

        self.activity_logger.change(f"Åpner port {port}")
        self.activate_relay(port)
        self._operation_flags[port]["moving"] = True
        self._operation_flags[port]["start_time"] = time.time()

        if self.testing_mode:
            self.sensor_event_callback(port, "open", 0)

        return {"port": port, "action": "open initiated"}

    def close_port(self, port):
        if self.status.get(port) == "closed":
            return {"port": port, "status": "already closed"}

        self.activity_logger.change(f"Lukker port {port}")
        self.activate_relay(port)
        self._operation_flags[port]["moving"] = True
        self._operation_flags[port]["start_time"] = time.time()

        if self.testing_mode:
            self.sensor_event_callback(port, "closed", 0)

        return {"port": port, "action": "close initiated"}

    def stop_port(self, port):
        if not self._operation_flags[port]["moving"]:
            return {"port": port, "status": "not moving"}

        self._operation_flags[port]["moving"] = False
        self.activity_logger.change(f"Stopper port {port}")
        return {"port": port, "status": "stopped"}
    
    def activate_relay(self, port):
        """
        Wrapper for trigger() med allerede tilgjengelig konfig og pi.
        """
        trigger(
            port=port,
            pi=self.pi,
            relay_pins=self.relay_pins,
            relay_config=self.relay_config,
            #logger=self.logger
        )

    def get_current_status(self, port):
        return self.status.get(port, "unknown")

    def get_all_status(self):
        """
        Returnerer status for alle porter som et dictionary.
        """
        return {port: self.get_current_status(port) for port in self.get_ports()}

    def get_port_names(self):
        return list(set(self.relay_pins.keys()) | set(self.config_gpio.get("sensor_pins", {}).keys()))

    
    def get_ports(self):
        return list(self.config_gpio.get("relay_pins", {}).keys())


    def get_reported_status(self, port):
        """
        Returnerer vurdert status for porten.
        Bruker sensorstatus og eventuell bevegelsesstatus.
        """
        if self._operation_flags[port]["moving"]:
            return "moving"

        status = self.status.get(port, "unknown")
        return status

    def _update_timing_data(self, port, direction, duration, t0=None, t1=None):
        """
        Oppdaterer timinginformasjon i config_system.json.
        """
        try:
            timing = self.config_system.setdefault(port, {}).setdefault("timing", {})
            timing_dir = timing.setdefault(direction, {})

            # Oppdater historikk
            history = timing_dir.setdefault("history", [])
            history.append(round(duration, 2))
            max_history = self.config_gpio.get("timing_config", {}).get("timing_history_size", 3)
            if len(history) > max_history:
                history.pop(0)

            # Beregn gjennomsnitt
            avg = round(sum(history) / len(history), 2)
            timing_dir["last"] = round(duration, 2)
            timing_dir["avg"] = avg

            if t0 is not None:
                timing_dir["t0"] = round(t0, 2)
            if t1 is not None:
                timing_dir["t1"] = round(t1, 2)
            timing_dir["t2"] = round(duration, 2)

            # Logg til timing.log
            self.timing_logger.timing(port, {
                "direction": direction,
                "t0": round(t0, 2) if t0 else None,
                "t1": round(t1, 2) if t1 else None,
                "t2": round(duration, 2),
                "avg": avg
            })

            self.save_config()
        except Exception as e:
            self.logger.error(f"Feil i _update_timing_data: {e}")



    def _write_config_to_disk(self):
        with open(paths.CONFIG_SYSTEM_PATH, "w") as f:
            json.dump(self.config_system, f, indent=2)

    def _handle_relay_timeout(self, port):
        flags = self._operation_flags.get(port, {})
        if flags.get("first_sensor_time") is None:
            self._set_status(port, self.status.get(port))  # behold forrige status
            self.status_logger.warning(port, "Ingen sensorrespons – motor trolig ikke aktivert")
            self.logger.error(port, "Puls sendt, men ingen sensor endret status")
            flags["moving"] = False

    def _handle_movement_timeout(self, port):
        flags = self._operation_flags.get(port, {})
        if flags.get("moving"):
            source = "system" if flags.get("stopped_by_system") else "manuell"
            self._set_status(port, "partial")
            self.logger.info(port, f"Port stoppet – delvis åpen (kilde: {source})")
            self.logger.error(port, f"{port} | bevegelse ikke fullført innen forventet tid | kilde: {source}")
            flags["moving"] = False

    def _sensor_callback(self, gpio, level, tick, port, sensor_type):
        """
        Callback-funksjon som trigges når en sensor endrer tilstand.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_logger.change(f"{port} {sensor_type} sensor endret: level={level} @ {timestamp}")

        if port not in self.status:
            self.logger.error(f"Ukjent port i callback: {port}")
            return

        direction = self._operation_flags[port].get("direction")
        start_time = self._operation_flags[port].get("start_time")

        if not self._operation_flags[port].get("moving"):
            # Sjekk om begge sensorene er inaktive → mulig port ble flyttet manuelt
            open_active = self.sensor_monitor.is_sensor_active(port, "open")
            closed_active = self.sensor_monitor.is_sensor_active(port, "closed")
            if not open_active and not closed_active:
                self.status[port] = "partial"
                self.status_logger.info(f"{port}: Manuell bevegelse? Ingen sensorer aktive.")
            return

        expected_sensor = "open" if direction == "open" else "closed"
        opposite_sensor = "closed" if direction == "open" else "open"
        now = time.time()

        # Registrer t0 dersom dette er første sensor-endring (sensor blir inaktiv)
        if "movement_detected_time" not in self._operation_flags[port] and sensor_type == opposite_sensor and level == 0:
            self._operation_flags[port]["movement_detected_time"] = now
            self.logger.debug(f"{port}: movement_detected_time satt ({sensor_type} = 0)")

        # Dette er "mål-sensoren" – porten ferdig åpnet/lukket
        if sensor_type == expected_sensor and level == self.sensor_monitor.active_state:
            movement_time = self._operation_flags[port].get("movement_detected_time")
            elapsed_total = now - start_time if start_time else None
            t0 = movement_time - start_time if start_time and movement_time else None
            t1 = elapsed_total - t0 if elapsed_total and t0 else None

            self._update_timing_data(port, direction, elapsed_total, t0, t1)
            self.status[port] = direction
            self.config_system[port]["status"] = direction
            self.config_system[port]["status_timestamp"] = timestamp

            self._operation_flags[port] = {
                "moving": False,
                "start_time": None,
                "direction": None,
                "movement_detected_time": None
            }

            self.status_logger.info(f"{port} er nå {direction}")
            self.save_config()

        elif sensor_type == opposite_sensor and level == self.sensor_monitor.active_state:
            self.status[port] = "partial"
            self._operation_flags[port] = {
                "moving": False,
                "start_time": None,
                "direction": None,
                "movement_detected_time": None
            }
        self.logger.warning(f"{port}: Motsatt sensor aktivert – manuell stopp eller avbrudd")

    def shutdown(self):
        if getattr(self, "_already_shutdown", False):
            return
        self._already_shutdown = True
        self.logger.debug("Shutdown pågår – rydder opp rele og sensorer")
        try:
            if hasattr(self.sensor_monitor, "cleanup"):
                self.sensor_monitor.cleanup()
        except Exception as e:
            self.logger.error("shutdown", f"Feil ved opprydding: {e}")
        else:
            self.logger.info("GarageController shutdown fullført.")