import os
import time
from utils.config_loader import load_config
from config import config_paths
from utils.garage_logger import get_logger

from sensors.bme280_sensor import BME280Sensor

logger = get_logger("sensor_manager")

class SensorManager:
    SENSOR_TYPES = {
        "BME280": BME280Sensor
    }

    def __init__(self):
        self.sensors = []
        self.status_file = config_paths.SENSOR_STATUS_PATH
        self.load_sensors()

    def load_sensors(self):
        try:
            config = load_config(config_paths.CONFIG_SENSORS_PATH)
            for sensor_conf in config.get("sensors", []):
                if not sensor_conf.get("enabled", True):
                    logger.log_status("SensorManager", f"Sensor '{sensor_conf['id']}' er deaktivert i config")
                    continue

                sensor_type = sensor_conf.get("type")
                cls = self.SENSOR_TYPES.get(sensor_type)
                if cls:
                    try:
                        self.sensors.append(cls(sensor_conf))
                        logger.log_status("SensorManager", f"Sensor '{sensor_conf['id']}' ({sensor_type}) lastet")
                    except Exception as e:
                        logger.log_error("SensorManager", f"Feil ved sensor '{sensor_conf['id']}': {e}")
                else:
                    logger.log_error("SensorManager", f"Ukjent sensortype: {sensor_type}")
        except Exception as e:
            logger.log_error("SensorManager", f"Feil ved lasting av sensorkonfigurasjon: {e}")

    def read_all(self):
        result = {}
        for sensor in self.sensors:
            data = sensor.read_data()
            if data:
                result[sensor.id] = data
        return result

    def save_latest(self, data):
        try:
            os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
            with open(self.status_file, "w") as f:
                import json
                json.dump(data, f, indent=2)
            logger.log_status("SensorManager", f"Lagret siste sensorverdier til {self.status_file}")
        except Exception as e:
            logger.log_error("SensorManager", f"Feil ved skriving av sensorstatus: {e}")
