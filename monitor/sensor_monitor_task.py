from utils.logging.unified_logger import get_logger
import time
import datetime
from sensors.environment_manager import EnvironmentSensorManager

logger = get_logger("EnvironmentSensorManager", category="system")
env_logger = get_logger("EnvironmentSensorManager", category="environment")



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
                    env_logger(sid, msg)
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Overvåking avsluttet manuelt")
    except Exception as e:
        logger.error(f"Uventet feil: {str(e)}")
