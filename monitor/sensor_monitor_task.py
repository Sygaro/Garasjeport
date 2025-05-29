import time
import datetime
from sensors.environment_manager import EnvironmentSensorManager
from utils.logging.logger_manager import get_logger

logger = get_logger("sensor_monitor", category="system")
env_logger = get_logger("environment", category="env")



def run_sensor_monitor_loop():
    """
    Løpende overvåking av sensorer. Leser verdier og logger/lagrer til statusfil.
    Håndterer dynamisk intervall for hver sensor via EnvironmentSensorManager.
    """
    sensor_manager = EnvironmentSensorManager()
    logger.status("SensorMonitor", "Starter sensor-overvåking...")

    try:
        while True:
            readings = sensor_manager.read_all()
            if readings:
                sensor_manager.save_latest(readings)
                for sid, values in readings.items():
                    msg = f"Temp: {values['temperature']}°C, Hum: {values['humidity']}%, Press: {values['pressure']} hPa"
                    env_logger(sid, msg)
            time.sleep(5)
    except KeyboardInterrupt:
        logger.status("SensorMonitor", "Overvåking avsluttet manuelt")
    except Exception as e:
        logger.error("SensorMonitor", f"Uventet feil: {str(e)}")
