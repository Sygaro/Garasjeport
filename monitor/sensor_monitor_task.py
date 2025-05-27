import time
import datetime
from sensors.sensor_manager import SensorManager
from utils.garage_logger import get_logger

logger = get_logger("sensor_monitor")

def run_sensor_monitor_loop():
    """
    Løpende overvåking av sensorer. Leser verdier og logger/lagrer til statusfil.
    Håndterer dynamisk intervall for hver sensor via SensorManager.
    """
    sensor_manager = SensorManager()
    logger.log_status("SensorMonitor", "Starter sensor-overvåking...")

    try:
        while True:
            readings = sensor_manager.read_all()
            if readings:
                sensor_manager.save_latest(readings)
                for sid, values in readings.items():
                    msg = f"Temp: {values['temperature']}°C, Hum: {values['humidity']}%, Press: {values['pressure']} hPa"
                    logger.log_sensor_data(sid, msg)
            time.sleep(5)
    except KeyboardInterrupt:
        logger.log_status("SensorMonitor", "Overvåking avsluttet manuelt")
    except Exception as e:
        logger.log_error("SensorMonitor", f"Uventet feil: {str(e)}")
