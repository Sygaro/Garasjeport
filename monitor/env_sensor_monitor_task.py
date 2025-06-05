from utils.logging.unified_logger import get_logger
import time
# import datetime
from sensors.environment_manager import EnvironmentSensorManager
from monitor.monitor_registry import register_monitor, update_monitor


logger = get_logger("env_sensor_mgmr", category="system")
env_logger = get_logger("env_sensor_mgmr", category="environment")



def run_sensor_monitor_loop():
    """
    Løpende overvåking av sensorer. Leser verdier og logger/lagrer til statusfil.
    Håndterer dynamisk intervall for hver sensor via EnvironmentSensorManager.
    """
    sensor_manager = EnvironmentSensorManager()
    logger.info("Starter sensor-overvåking...")

    try:
        while True:
            readings = sensor_manager.read_all()
            if readings:
                sensor_manager.save_latest(readings)
                for sid, values in readings.items():
                    msg = f"Temp: {values['temperature']}°C, Hum: {values['humidity']}%, Press: {values['pressure']} hPa"
                    env_logger.info(f"{sid}: {msg}")
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Overvåking avsluttet manuelt")
    except Exception as e:
        logger.error(f"Uventet feil: {str(e)}")

def monitor_loop():
    register_monitor("env_sensor_monitor")
    logger.info("Starter overvåking av miljøsensorer...")
    while True:
        update_monitor("env_sensor_monitor")
        logger.debug("Oppdaterer monitor status")