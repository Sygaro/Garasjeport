
# Fil: garage_controller.py
# Modul for portkontroll: åpne/lukke porter, lese status, og måle bevegelsestid

import time
import RPi.GPIO as GPIO
from event_log import log_event

GPIO.cleanup()  # rydder gamle eventer

class GarageController:

    def init_sensor_events(self):
        for port, sensorer in self.sensor_pins.items():
            for posisjon, pin in sensorer.items():
                self.legg_til_event(pin, self._sensor_callback)
        print("✔️ Alle sensor-GPIO-eventer registrert.")

    def __init__(self, config):
        import RPi.GPIO as GPIO
        from garage_controller import sensor_callback  # sikrer tilgang

        self.config = config
        self.relay_pins = config.get("relay_pins", {})
        self.sensor_pins = config.get("sensor_pins", {})
        self.init_sensor_events()

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Sett opp releer
        for pin in self.relay_pins.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)  # Relé inaktiv ved oppstart

        # Sett opp sensorer og event detection
        for port, sensors in self.sensor_pins.items():
            for sensor_pin in sensors.values():
                try:
                    GPIO.setup(sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                    log_event("debug", f"✅ Setup OK for GPIO {sensor_pin} – nå prøver vi å legge til event")
                    GPIO.add_event_detect(sensor_pin, GPIO.BOTH, callback=sensor_callback, bouncetime=200)
                except RuntimeError as e:
                    log_event("debug", f"⚠️ Feil ved GPIO {sensor_pin} for port {port}: {e}")



    def _sensor_callback(self, pin):
        print(f"📟 Sensor-endring oppdaget på GPIO {pin}")

    def legg_til_event(self, pin, callback):
        try:
            GPIO.remove_event_detect(pin)
        except RuntimeError:
            pass
        try:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=callback, bouncetime=200)
            print(f"✔️ Registrerte edge-detection for GPIO {pin}")
        except RuntimeError as e:
            print(f"❌ Feil ved registrering av edge detection for GPIO {pin}: {e}")

    def cleanup(self):
        GPIO.cleanup()


    def update_config(self, new_config):
        """Oppdaterer GPIO-oppsettet ved endringer i config.json"""
        import RPi.GPIO as GPIO
        from garage_controller import sensor_callback  # sørg for at denne er tilgjengelig

        old_relays = self.relay_pins
        old_sensors = self.sensor_pins

        new_relays = new_config.get("relay_pins", {})
        new_sensors = new_config.get("sensor_pins", {})

        # 🔁 Rydd gamle relé-pinner som ikke lenger er i bruk
        for port, pin in old_relays.items():
            if port not in new_relays or new_relays[port] != pin:
                GPIO.cleanup(pin)

        # 🔁 Rydd gamle sensor-pinner som ikke lenger er i bruk
        for port, sensors in old_sensors.items():
            for pos, pin in sensors.items():
                if (
                    port not in new_sensors
                    or pos not in new_sensors[port]
                    or new_sensors[port][pos] != pin
                ):
                    GPIO.cleanup(pin)

        # ✅ Oppdater og sett opp nye relé-pinner
        for port, pin in new_relays.items():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)

        # ✅ Oppdater og sett opp nye sensor-pinner
        for port, sensors in new_sensors.items():
            for pos, pin in sensors.items():
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                try:
                    GPIO.add_event_detect(pin, GPIO.BOTH, callback=sensor_callback, bouncetime=200)
                except RuntimeError as e:
                    print(f"⚠️ Feil ved GPIO {pin} for port {port}: {e}")

        # 💾 Lagre ny konfig internt
        self.relay_pins = new_relays
        self.sensor_pins = new_sensors
        self.config = new_config



    def open_port(self, port):
        pin = self.relay_pins.get(port)
        if pin is None:
            log_event("error", f"Ugyldig portnavn: {port}")
            return False

        log_event("action", f"Sender åpen/lukk-impuls til {port}", data={"gpio": pin})
        GPIO.output(pin, GPIO.LOW)
        time.sleep(self.config.get("relay_pulse_length", 0.5))
        GPIO.output(pin, GPIO.HIGH)
        return True

    def get_port_status(self, port):
        """
        Returnerer status for en port basert på to sensorer (aktiv = 0 med PUD_UP).
        """
        pins = self.sensor_pins.get(port)
        if not pins:
            return "ukjent"

        open_state = GPIO.input(pins.get("open"))     # 0 = aktiv
        closed_state = GPIO.input(pins.get("closed")) # 0 = aktiv

        if open_state == 0 and closed_state == 1:
            return "åpen"
        elif open_state == 1 and closed_state == 0:
            return "lukket"
        elif open_state == 1 and closed_state == 1:
            return "ukjent"  # ingen sensor aktiv
        elif open_state == 0 and closed_state == 0:
            return "sensorfeil"  # begge aktive
        else:
            return "ukjent"


    def maal_aapnetid(self, port, timeout=60):
        """Måler tid fra port starter åpning til åpen-sensor er aktiv."""
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
            if GPIO.input(sensors.get("open")):
                return time.time() - start
            time.sleep(0.1)

        return None

    def maal_lukketid(self, port, timeout=60):
        """Måler tid fra port starter lukking til lukket-sensor er aktiv."""
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
            if GPIO.input(sensors.get("closed")):
                return time.time() - start
            time.sleep(0.1)

        return None

    def send_pulse(self, port):
        """Sender et kort puls-signal til reléet for angitt port."""
        import time
        pin = self.relay_pins.get(port)
        if pin is None:
            raise ValueError(f"Ukjent port: {port}")
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.3)  # juster ved behov
        GPIO.output(pin, GPIO.HIGH)

    def read_sensor(self, port, position):
        """Leser sensorverdi for 'open' eller 'closed' posisjon på gitt port."""
        pin = self.sensor_pins.get(port, {}).get(position)
        if pin is None:
            raise ValueError(f"Sensor '{position}' mangler for port: {port}")
        return GPIO.input(pin)


    def try_send_pulse(self, port, action="open"):
        """
        Kontrollerer portstatus før rele-aktivering.
        Returnerer (success: bool, message: str)
        """
        import time
        status = self.get_port_status(port)

        if action == "open":
            if status == "åpen":
                return False, "Porten er allerede åpen"
            elif status == "sensorfeil":
                return False, "Sensorfeil – portstatus kan ikke bekreftes"
            elif status == "ukjent":
                return False, "ukjent"  # app.py håndterer dette
        elif action == "close":
            if status == "lukket":
                return False, "Porten er allerede lukket"
            elif status == "sensorfeil":
                return False, "Sensorfeil – portstatus kan ikke bekreftes"
            elif status == "ukjent":
                return False, "ukjent"

        # Send puls til rele
        pin = self.relay_pins.get(port)
        if pin is None:
            return False, f"Port {port} finnes ikke"

        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.3)
        GPIO.output(pin, GPIO.HIGH)
        return True, f"Signal sendt – porten forsøkes {action}et"

    def send_pulse_raw(self, port):
        """Sender puls direkte til releet uten statuskontroll (brukes ved ukjent status)."""
        import time
        pin = self.relay_pins.get(port)
        if pin is None:
            raise ValueError(f"Port {port} finnes ikke")
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.3)
        GPIO.output(pin, GPIO.HIGH)


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

