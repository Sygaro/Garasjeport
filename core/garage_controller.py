import time
import threading

from utils.relay_control import RelayControl
from utils.garage_logger import GarageLogger

# Forsøk å importere pigpio-monitor, fallback til None hvis ikke tilgjengelig
try:
    from utils.sensor_monitor import SensorMonitor
except ImportError:
    SensorMonitor = None


class GarageController:
    """
    Hovedklassen for styring av garasjeporter via rele og magnetsensorer.
    Bruker pigpio for edge detection, og støtter testing-modus uten fysisk maskinvare.
    """

    def __init__(self, config_gpio, config_system, testing_mode=False):
        """
        Initierer kontroller for porter, logger og sensorer.
        :param config_gpio: GPIO-konfigurasjon fra JSON
        :param config_system: Systeminnstillinger fra JSON
        :param testing_mode: True = simulerer sensorrespons uten fysisk maskinvare
        """
        self.config_gpio = config_gpio
        self.config_system = config_system
        self.testing_mode = testing_mode

        self.status = {}  # Lagrer status for hver port (open/closed/moving)
        self.logger = GarageLogger()
        self.relay_control = RelayControl(config_gpio)

        self.sensor_monitor = None

        # Oppstart: Sensorovervåkning
        if self.testing_mode:
            print("[TESTMODE] pigpio deaktiveres – sensorer simuleres")
        elif SensorMonitor:
            try:
                self.sensor_monitor = SensorMonitor(
                    self.config_gpio["sensor_pins"],
                    self.sensor_event_callback
                )
                print("[INIT] pigpio SensorMonitor aktivert")
            except Exception as e:
                print(f"[ERROR] Kunne ikke starte SensorMonitor: {e}")
        else:
            print("[WARNING] SensorMonitor ikke tilgjengelig")

        self._init_port_statuses()

    def _init_port_statuses(self):
        """
        Setter initial status for porter til 'unknown'
        """
        for port in self.config_gpio["sensor_pins"]:
            self.status[port] = "unknown"

    def get_current_status(self, port):
        """
        Returnerer nåværende status for en spesifikk port
        :param port: Navn på port
        :return: Status-streng
        """
        return self.status.get(port, "unknown")

    def get_all_statuses(self):
        """
        Returnerer alle portstatusene som dictionary
        :return: Dict {portnavn: status}
        """
        return self.status

    def sensor_event_callback(self, port, sensor_type, level):
        """
        Kalles av pigpio (eller testmodus) når en sensor endrer tilstand.
        Oppdaterer portstatus basert på sensor-type og aktiv tilstand.
        :param port: Portnavn
        :param sensor_type: "open" eller "closed"
        :param level: GPIO-nivå (0 = aktiv ved pullup)
        """
        active_state = self.config_gpio["sensor_config"]["active_state"]
        is_active = (level == active_state)

        log_msg = f"{port} | sensor: {sensor_type} | level: {level} | active: {is_active}"
        self.logger.log_status(log_msg)

        # Oppdater portstatus
        if sensor_type == "open" and is_active:
            self.status[port] = "open"
        elif sensor_type == "closed" and is_active:
            self.status[port] = "closed"
        elif not is_active:
            self.status[port] = "moving"

        print(f"[EDGE] {port}: {sensor_type} → {'aktiv' if is_active else 'inaktiv'} | status: {self.status[port]}")

    def open_port(self, port):
        """
        Åpner porten ved å aktivere releet og venter på at 'open'-sensor trigges.
        :param port: Navn på port
        """
        self.logger.log_action(f"Åpner port {port}")
        self.relay_control.trigger(port)

        if self.testing_mode:
            threading.Timer(1, lambda: self.sensor_event_callback(port, "open", 0)).start()

    def close_port(self, port):
        """
        Lukker porten ved å aktivere releet og venter på at 'closed'-sensor trigges.
        :param port: Navn på port
        """
        self.logger.log_action(f"Lukker port {port}")
        self.relay_control.trigger(port)

        if self.testing_mode:
            threading.Timer(1, lambda: self.sensor_event_callback(port, "closed", 0)).start()

    def cleanup(self):
        """
        Rydding ved avslutning – avslutter sensorovervåkning og rele.
        """
        if self.sensor_monitor:
            self.sensor_monitor.stop()
        self.relay_control.cleanup()
