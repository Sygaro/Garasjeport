# ========================================
# Filnavn: garage_controller.py
# Garasjeport-kontroller – styrer porter via rele og sensorer
# ========================================

import lgpio, os, json
import time

from datetime import datetime
from config.config_paths import CONFIG_GPIO_PATH, CONFIG_SYSTEM_PATH
from core.garage_logger import GarageLogger
from utils.file_utils import load_json, save_json


# print("[DEBUG] Laster GarageController fra:", __file__)

class GarageController:
    def __init__(self):
        self.chip = lgpio.gpiochip_open(0)
        self.logger = GarageLogger()
        self.config = self._load_gpio_config()

        self.relay_pins = self.config.get("relay_pins", {})
        self.sensor_pins = self.config.get("sensor_pins", {})
        self.fail_margin = 3  # sekunder, konfigurerbar senere

        self._setup_pins()

        print("[GarageController] Initialisert med følgende pinner:")
        for port, pin in self.relay_pins.items():
            print(f"  🔁 Rele - {port}: GPIO {pin}")
        for port, sensors in self.sensor_pins.items():
            print(f"  🧲 Sensorer - {port}: Åpen={sensors.get('open')} | Lukket={sensors.get('closed')}")


    def _load_gpio_config(self):
        try:
            with open(CONFIG_GPIO_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[GarageController] Feil ved lasting av GPIO-config: {e}")
            return {}

    def _setup_pins(self):
        print("[GarageController] Setter opp rele-pinner...")
        for port, pin in self.relay_pins.items():
            try:
                lgpio.gpio_claim_output(self.chip, pin)
                print(f"  ✅ Rele-pin for {port}: GPIO {pin}")
            except Exception as e:
                print(f"  ❌ Feil ved oppsett av rele-pin for {port} (GPIO {pin}): {e}")

        print("[GarageController] Setter opp sensor-pinner...")
        for port in self.sensor_pins:
            for sensor_type, pin in self.sensor_pins[port].items():
                try:
                    lgpio.gpio_claim_input(self.chip, pin, lgpio.SET_PULL_UP)
                    print(f"  ✅ Sensor-pin ({sensor_type}) for {port}: GPIO {pin}")
                except Exception as e:
                    print(f"  ❌ Feil ved oppsett av sensor-pin ({sensor_type}) for {port} (GPIO {pin}): {e}")


    def is_sensor_active(self, pin):
        return lgpio.gpio_read(self.chip, pin) == 0  # Aktiv lav

    def get_current_status(self, port):
        """
        Returnerer status for gitt port basert på sensorverdier.
        Sensorene er normalt HIGH (1) og blir aktive ved LOW (0).
        """
        if port not in self.sensor_pins:
            return "unknown"

        open_pin = self.sensor_pins[port]["open"]
        closed_pin = self.sensor_pins[port]["closed"]

        open_active = not lgpio.gpio_read(self.chip, open_pin)
        closed_active = not lgpio.gpio_read(self.chip, closed_pin)

        if open_active and not closed_active:
            return "open"
        elif closed_active and not open_active:
            return "closed"
        elif not open_active and not closed_active:
            return "moving"
        elif open_active and closed_active:
            return "sensor_error"
        return "unknown"


    def pulse_relay(self, port, duration=0.5):
        pin = self.relay_pins.get(port)
        if pin is None:
            raise ValueError(f"Ugyldig port: {port}")
        lgpio.gpio_write(self.chip, pin, 1)
        time.sleep(duration)
        lgpio.gpio_write(self.chip, pin, 0)

    def open_port(self, port):
        status = self.get_current_status(port)
        if status == "open":
            return {"status": "already_open"}

        if status == "sensor_error":
            return {"status": "sensor_error", "confirm_required": True}

        if status == "partial":
            return {"status": "unknown_position", "confirm_required": True}

        self.logger.log_action(port, "open", source="api")
        self.pulse_relay(port)

        timing = self._measure_motion_time(port, direction="open")
        return {"status": "opening", **timing}

    def close_port(self, port):
        status = self.get_current_status(port)
        if status == "closed":
            return {"status": "already_closed"}

        if status == "sensor_error":
            return {"status": "sensor_error", "confirm_required": True}

        if status == "partial":
            return {"status": "unknown_position", "confirm_required": True}

        self.logger.log_action(port, "close", source="api")
        self.pulse_relay(port)

        timing = self._measure_motion_time(port, direction="close")
        return {"status": "closing", **timing}

    def _measure_motion_time(self, port, direction):
        pins = self.sensor_pins.get(port, {})
        open_pin = pins.get("open")
        closed_pin = pins.get("closed")

        if direction == "open":
            sensor_1 = closed_pin
            sensor_2 = open_pin
        else:
            sensor_1 = open_pin
            sensor_2 = closed_pin

        start = time.time()

        # Vent til første sensor slipper (motor har startet)
        while self.is_sensor_active(sensor_1):
            if time.time() - start > 10:  # fail-safe
                return {"error": "timeout_step1"}
            time.sleep(0.05)
        rele_delay = time.time() - start

        # Vent til neste sensor aktiveres
        while not self.is_sensor_active(sensor_2):
            if time.time() - start > 30:
                return {"error": "timeout_step2"}
            time.sleep(0.05)
        total = time.time() - start
        sensor_to_sensor = total - rele_delay

        self.logger.log_timing(port, direction, total)
        self._update_timing(port, direction, total)
        return {
            "rele_delay": round(rele_delay, 2),
            "sensor_to_sensor": round(sensor_to_sensor, 2),
            "total": round(total, 2),
            "timestamp": datetime.now().isoformat()
        }

    def cleanup(self):
        print("[GarageController] Frigjør GPIO-pinner...")
        for pin in self.relay_pins.values():
            try:
                lgpio.gpio_free(self.chip, pin)
            except Exception as e:
                print(f"Feil ved frigjøring av rele-pin {pin}: {e}")
        for port in self.sensor_pins:
            for pin in self.sensor_pins[port].values():
                try:
                    lgpio.gpio_free(self.chip, pin)
                except Exception as e:
                    print(f"Feil ved frigjøring av sensor-pin {pin}: {e}")
        try:
            lgpio.gpiochip_close(self.chip)
        except Exception as e:
            print(f"Feil ved lukking av chip: {e}")

    def get_current_status(self, port):
        """
        Returnerer status for gitt port basert på sensorverdier.
        """
        if port not in self.sensor_pins:
            return "unknown"

        open_pin = self.sensor_pins[port]["open"]
        closed_pin = self.sensor_pins[port]["closed"]

        open_active = not lgpio.gpio_read(self.chip, open_pin)
        closed_active = not lgpio.gpio_read(self.chip, closed_pin)

        if open_active and not closed_active:
            return "open"
        elif closed_active and not open_active:
            return "closed"
        elif not open_active and not closed_active:
            return "moving"
        elif open_active and closed_active:
            return "sensor_error"
        else:
            return "unknown"


    def save_port_timing(self, port, direction, duration):
        """
        Lagre sist målte åpne/lukketid til config_system.json
        """
        try:
            with open(CONFIG_SYSTEM_PATH, "r") as f:
                config = json.load(f)
        except Exception as e:
            print(f"[GarageController] Kunne ikke lese config_system.json: {e}")
            return

        if "port_timings" not in config:
            config["port_timings"] = {}

        if port not in config["port_timings"]:
            config["port_timings"][port] = {}

        config["port_timings"][port][f"{direction}_time"] = round(duration, 2)
        config["port_timings"][port]["timestamp"] = datetime.now().isoformat()

        try:
            with open(CONFIG_SYSTEM_PATH, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"[GarageController] Kunne ikke skrive til config_system.json: {e}")

    def get_port_timing(self, port):
        try:
            with open(CONFIG_SYSTEM_PATH, "r") as f:
                config = json.load(f)
            return config.get("port_timings", {}).get(port, {})
        except:
            return {}


    def activate_port(self, port: str, direction: str):
        """
        Aktiverer rele for gitt port, måler tid og oppdaterer timing-data.
        direction = 'open' eller 'close'
        """
        print(f"[GarageController] Starter bevegelse på {port} ({direction})")

        if port not in self.relay_pins or port not in self.sensor_pins:
            print(f"[GarageController] ❌ Ugyldig port: {port}")
            return {"success": False, "error": "Ugyldig port"}

        # 1. Sjekk status før aktivering
        current_status = self.get_current_status(port)
        if direction == "open" and current_status == "open":
            return {"success": False, "message": f"{port} er allerede åpen"}
        if direction == "close" and current_status == "closed":
            return {"success": False, "message": f"{port} er allerede lukket"}

        # 2. Send puls
        pin = self.relay_pins[port]
        lgpio.gpio_write(self.chip, pin, 1)
        time.sleep(0.2)  # 200 ms puls
        lgpio.gpio_write(self.chip, pin, 0)
        self.logger.log_action(port, action=direction)

        # 3. Start tidtaking
        t0 = time.time()
        timeout = self.get_expected_time(port, direction) + self.fail_margin
        reached = False
        expected_sensor = self.sensor_pins[port]["open"] if direction == "open" else self.sensor_pins[port]["closed"]

        print(f"[GarageController] Venter på sensor-endring på GPIO{expected_sensor}...")

        while time.time() - t0 < timeout:
            level = lgpio.gpio_read(self.chip, expected_sensor)
            if level == 1:
                reached = True
                break
            time.sleep(0.1)

        duration = round(time.time() - t0, 2)

        # 4. Evaluer
        if reached:
            self.logger.log_timing(port, direction, duration)
            self._update_port_timing(port, direction, duration)
            return {"success": True, "duration": duration}
        else:
            self.logger.log_status_change(port, "delvis_åpen")
            return {"success": False, "error": "Timeout – porten nådde ikke ønsket posisjon", "duration": duration}

    def get_expected_time(self, port, direction):
        timings = load_json(CONFIG_SYSTEM_PATH).get("port_timings", {})
        return timings.get(port, {}).get(f"{direction}_time", 60)

    def _update_port_timing(self, port, direction, duration):
        config = load_json(CONFIG_SYSTEM_PATH)
        config.setdefault("port_timings", {})
        config["port_timings"].setdefault(port, {})
        config["port_timings"][port][f"{direction}_time"] = duration
        config["port_timings"][port]["timestamp"] = datetime.now().isoformat()
        save_json(CONFIG_SYSTEM_PATH, config)



def _load_system_config(self):
    if not os.path.exists(CONFIG_SYSTEM_PATH):
        return {}
    try:
        with open(CONFIG_SYSTEM_PATH) as f:
            return json.load(f)
    except:
        return {}

def _save_system_config(self, config):
    with open(CONFIG_SYSTEM_PATH, "w") as f:
        json.dump(config, f, indent=2)

def _update_timing(self, port, direction, duration):
    config = self._load_system_config()
    if "timing" not in config:
        config["timing"] = {}
    if port not in config["timing"]:
        config["timing"][port] = {}

    config["timing"][port][direction] = {
        "duration": round(duration, 2),
        "timestamp": datetime.now().isoformat()
    }

    self._save_system_config(config)




