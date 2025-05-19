# ==========================================
# Filnavn: garage_controller.py
# Modul: Kontroller for garasjeporter (GPIO)
# ==========================================

import time
import lgpio
import threading
import json
import os
from datetime import datetime

from config.config_paths import CONFIG_GPIO_PATH, CONFIG_SYSTEM_PATH
from utils.file_utils import load_json, save_json
from utils.garage_logger import GarageLogger


class GarageController:
    def __init__(self):
        print("[GarageController] Initialiserer...")

        self.chip = lgpio.gpiochip_open(0)
        self.logger = GarageLogger()

        self.gpio_config = load_json(CONFIG_GPIO_PATH)
        self.system_config = load_json(CONFIG_SYSTEM_PATH)

        self.relay_pins = self.gpio_config.get("relay_pins", {})
        self.sensor_pins = self.gpio_config.get("sensor_pins", {})
        self.relay_config = self.gpio_config.get("relay_config", {})
        self.sensor_config = self.gpio_config.get("sensor_config", {})
        self.timing_cfg = self.gpio_config.get("timing_config", {})

        self.pulse_duration = self.relay_config.get("pulse_duration", 0.4)
        self.relay_active_state = self.relay_config.get("active_state", 0)

        self.sensor_active = self.sensor_config.get("active_state", 0)
        self.pull = self.sensor_config.get("pull", "up")
        self.pull_val = lgpio.SET_PULL_UP if self.pull == "up" else lgpio.SET_PULL_DOWN
        self._recent_pulse = False  # brukes til dynamisk polling


        self.fast_poll = self.timing_cfg.get("fast_poll_interval", 0.01)
        self.slow_poll = self.timing_cfg.get("slow_poll_interval", 2.0)
        self.timeout = self.timing_cfg.get("port_status_change_timeout", 60)
        self._last_known_status = {port: "unknown" for port in self.relay_pins}
        self.fail_margin = self.timing_cfg.get("fail_margin_status_change", 5)
        self.port_status_timeout = self.gpio_config.get("relay_config", {}).get("port_status_change_timeout", 10)


        self._setup_pins()

        import threading

        # Etter self.last_known_status
        self.polling_active = True
        self.polling_thread = threading.Thread(target=self._sensor_poll_loop, daemon=True)
        self.polling_thread.start()



    def _setup_pins(self):
        print("[GarageController] Setter opp rele-pinner...")
        for port, pin in self.relay_pins.items():
            lgpio.gpio_claim_output(self.chip, pin, 1 - self.relay_active_state)
            print(f"  ✅ Rele-pin for {port}: GPIO {pin}")

        print("[GarageController] Setter opp sensor-pinner...")
        for port, sensors in self.sensor_pins.items():
            for label, pin in sensors.items():
                lgpio.gpio_claim_input(self.chip, pin, self.pull_val)
                print(f"  ✅ Sensor ({label}) for {port}: GPIO {pin}")

    def pulse_relay(self, port, duration=None):
        """Sender puls til rele for å aktivere motor."""
        pin = self.relay_pins.get(port)
        duration = duration if duration else self.pulse_duration
        if pin is None:
            raise ValueError(f"Ugyldig port: {port}")

        lgpio.gpio_write(self.chip, pin, self.relay_active_state)
        time.sleep(duration)
        lgpio.gpio_write(self.chip, pin, 1 - self.relay_active_state)

        self.logger.log_action(port, "relay_pulse", source="system")

    def get_current_status(self, port):
        """
        Leser sensorverdier og returnerer aktuell status for porten.
        Logger statusendringer.
        """
        if port not in self.sensor_pins:
            return "unknown"

        pins = self.sensor_pins[port]
        open_pin = pins["open"]
        closed_pin = pins["closed"]
        active = self.sensor_config.get("active_state", 0)

        open_active = (lgpio.gpio_read(self.chip, open_pin) == active)
        closed_active = (lgpio.gpio_read(self.chip, closed_pin) == active)

        if open_active and not closed_active:
            new_status = "open"
        elif closed_active and not open_active:
            new_status = "closed"
        elif not open_active and not closed_active:
            new_status = "moving"
        elif open_active and closed_active:
            new_status = "sensor_error"
        else:
            new_status = "unknown"

        prev_status = self._last_known_status.get(port)
        if new_status != prev_status:
            self.logger.log_status_change(port, new_status)
            self._last_known_status[port] = new_status

        return new_status


    def activate_port(self, port, direction):
        """
        Aktiverer port og måler total bevegelsestid. Avbryter ved feil.
        """
        start_status = self.get_current_status(port)
        target_status = "open" if direction == "open" else "closed"

        if start_status == target_status:
            return {"status": start_status, "note": "Allerede i ønsket posisjon"}

        self.logger.log_action(port, f"{direction}_start")
        self.pulse_relay(port)

        t0 = time.time()
        sensor_delay_threshold = self.relay_config.get("max_sensor_start_delay", 2)  # sekunder

        # Trinn 1: vent på første sensorendring (port begynner å bevege seg)
        while time.time() - t0 < sensor_delay_threshold:
            current = self.get_current_status(port)
            if current not in [start_status, "unknown"]:
                break  # port begynte å bevege seg
            time.sleep(self.fast_poll)
        else:
            # Timeout: port responderte ikke
            self.logger.log_error(port, "Ingen sensorrespons etter puls – port starter ikke")
            return {
                "status": "stopped",
                "error": f"Ingen sensorrespons innen {sensor_delay_threshold}s"
            }

        # Trinn 2: vent til port når sluttposisjon
        while time.time() - t0 < self.port_status_timeout:
            current = self.get_current_status(port)
            if current == target_status:
                duration = round(time.time() - t0, 2)
                self._store_timing(port, direction, duration)
                self.logger.log_timing(port, direction, duration)
                return {"status": current, "duration": duration}
            time.sleep(self.fast_poll)

        # Timeout: port stoppet på vei
        self.logger.log_error(port, "Tidsavbrudd – porten nådde ikke målet")
        self._last_known_status[port] = "stopped"
        return {"status": "stopped", "error": "Port endret ikke status"}


    def _store_timing(self, port, direction, duration):
        """
        Lagrer målt åpne-/lukketid + tidsstempel i config_system.json
        """
        config = load_json(CONFIG_SYSTEM_PATH)
        if "timing" not in config:
            config["timing"] = {}

        if port not in config["timing"]:
            config["timing"][port] = {}

          # ✅ Rund av duration til 2 desimaler før lagring
        config["timing"][port][f"{direction}_time"] = round(duration, 2)
        config["timing"][port][f"{direction}_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        save_json(CONFIG_SYSTEM_PATH, config)


    def open_port(self, port):
        """
        Utfører sikker åpning av port.
        Validerer status, logger og måler tid.
        """
        current_status = self.get_current_status(port)

        if current_status == "open":
            return {"status": "open", "note": "Porten er allerede åpen."}

        elif current_status == "sensor_error":
            self.logger.log_error(port, "Sensorfeil oppdaget før åpning – fortsetter likevel")
            return self.activate_port(port, direction="open")

        elif current_status == "moving":
            return {"status": "moving", "note": "Porten er i bevegelse – åpning avbrutt"}

        elif current_status == "unknown":
            self.logger.log_error(port, "Ukjent status før åpning – avbryter")
            return {"status": "unknown", "error": "Kan ikke bestemme portstatus"}

        # Ellers: forsøk å åpne
        return self.activate_port(port, direction="open")

    def close_port(self, port):
        """
        Utfører sikker lukking av port.
        Validerer status, logger og måler tid.
        """
        current_status = self.get_current_status(port)

        if current_status == "closed":
            return {"status": "closed", "note": "Porten er allerede lukket."}

        elif current_status == "sensor_error":
            self.logger.log_error(port, "Sensorfeil oppdaget før lukking – fortsetter likevel")
            return self.activate_port(port, direction="close")

        elif current_status == "moving":
            return {"status": "moving", "note": "Porten er i bevegelse – lukking avbrutt"}

        elif current_status == "unknown":
            self.logger.log_error(port, "Ukjent status før lukking – avbryter")
            return {"status": "unknown", "error": "Kan ikke bestemme portstatus"}

        # Ellers: forsøk å lukke
        return self.activate_port(port, direction="close")

    def stop_port(self, port):
        """
        Stopper motoren hvis porten er i bevegelse (begge sensorer inaktive).
        Returnerer suksessstatus og oppdatert portstatus.
        """
        current_status = self.get_current_status(port)

        if current_status != "moving":
            return {"success": False, "status": current_status, "note": "Porten er ikke i bevegelse"}

        self.logger.log_action(port, "stop_motor", source="API")

        # Send kort puls for å stoppe
        self.pulse_relay(port)

        # Merk portstatus som "stopped" manuelt
        self._last_known_status[port] = "stopped"

        return {"success": True, "status": "stopped", "note": "Motor stoppet"}


    def get_reported_status(self, port):
        """
        Returnerer siste status. Hvis status er 'stopped',
        sjekker sensorene om port faktisk er i sluttposisjon og oppdaterer.
        """
        status = self._last_known_status.get(port, "unknown")

        if status == "stopped":
            corrected = self.get_current_status(port)  # denne logger automatisk endringer
            if corrected in ["open", "closed"]:
                return corrected
            return "stopped"

        return status

    def get_cached_status(self, port):
        """
        Returnerer sist kjente status fra sensorpolling,
        faller tilbake til realtidsavlesning hvis ikke tilgjengelig.
        """
        return self._last_known_status.get(port, self.get_current_status(port))


    def _sensor_poll_loop(self):
        """
        Bakgrunnstråd som kontinuerlig overvåker sensorstatus og logger endringer.
        Justerer pollinghastighet basert på portstatus.
        """
        last_status = {}
        moving_since = {}

        while self.polling_active:
            interval = self.fast_poll if self._recent_pulse else self.slow_poll

            for port in self.sensor_pins:
                current = self.get_current_status(port)
                prev = last_status.get(port)

                if current != prev:
                    self.logger.log_status_change(port, current)
                    last_status[port] = current
                    if current == "moving":
                        moving_since[port] = time.time()
                    elif port in moving_since:
                        del moving_since[port]

                # Timeout: if in "moving" too long → mark as "stopped"
                if current == "moving":
                    start_time = moving_since.get(port)
                    if start_time and (time.time() - start_time) > self.timeout:
                        self.logger.log_status_change(port, "stopped")
                        last_status[port] = "stopped"
                        # Set as attribute if needed elsewhere
                        self._last_known_status[port] = "stopped"
                        # Important: remove from moving tracking
                        del moving_since[port]

            time.sleep(interval)



    def cleanup(self):
        """Frigjør GPIO og rydder opp ved avslutning."""
        print("[GarageController] Starter opprydding...")

        # Stopp sensorpolling først
        self.polling_active = False
        time.sleep(self.slow_poll + 0.1)

        # Frigi alle pins (før vi lukker chip)
        for pin in self.relay_pins.values():
            try:
                lgpio.gpio_free(self.chip, pin)
            except Exception as e:
                print(f"[GPIO Free] Kunne ikke frigjøre rele-pin {pin}: {e}")

        for sensors in self.sensor_pins.values():
            for pin in sensors.values():
                try:
                    lgpio.gpio_free(self.chip, pin)
                except Exception as e:
                    print(f"[GPIO Free] Kunne ikke frigjøre sensor-pin {pin}: {e}")

        # Lukk chip til slutt
        try:
            if hasattr(self, "chip") and isinstance(self.chip, int):
                lgpio.gpiochip_close(self.chip)
                print("[GarageController] GPIO chip lukket.")
        except Exception as e:
            print(f"[GarageController] Feil ved lukking av GPIO chip: {e}")
