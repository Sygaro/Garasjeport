import os
import time
import threading
import json
from datetime import datetime, time as dt_time
from utils.config_loader import load_config
from config import config_paths
from utils.logging.unified_logger import get_logger
from sensors.bme280_sensor import BME280Sensor


class EnvironmentSensorManager:
    SENSOR_TYPES = {
        "BME280": BME280Sensor
    }

    def __init__(self):

        self.status_logger = get_logger("env_manager", category="system")
        self.sensors = []
        self.status_file = config_paths.STATUS_SENSOR_ENV_PATH
        self.averages_file = config_paths.LOG_SENSOR_ENV_AVERAGES_PATH
        self.logging_enabled = True
        self.log_interval = 5
        self.buffer = {}
        self.load_sensors()
        self.load_config()
        self.start_logging_loop()
        self.last_hour = datetime.now().hour

    def load_sensors(self):
        try:
            config = load_config(config_paths.CONFIG_SENSOR_ENV_PATH)
            for sensor_conf in config.get("sensors", []):
                if not sensor_conf.get("enabled", True):
                    self.status_logger.info(f"Sensor '{sensor_conf['id']}' er deaktivert i config")
                    continue

                sensor_type = sensor_conf.get("type")
                cls = self.SENSOR_TYPES.get(sensor_type)
                if cls:
                    try:
                        self.sensors.append(cls(sensor_conf))
                        self.status_logger.info(f"Sensor '{sensor_conf['id']}' ({sensor_type}) lastet")
                        self.buffer[sensor_conf['id']] = []
                    except Exception as e:
                        self.status_logger.error(f"Feil ved sensor '{sensor_conf['id']}': {e}")
                else:
                    self.status_logger.error(f"Ukjent sensortype: {sensor_type}")
        except Exception as e:
            self.status_logger.error(f"Feil ved lasting av sensorkonfigurasjon: {e}")

    def load_config(self):
        try:
            config = load_config(config_paths.CONFIG_SENSOR_ENV_PATH)
            avg_config = config.get("averaging", {})
            self.log_interval = int(3600 / avg_config.get("samples_per_hour", 15))
            self.day_start = avg_config.get("day_range", {}).get("start", "06:00")
            self.day_end = avg_config.get("day_range", {}).get("end", "21:00")
            self.status_logger.info(f"Averaging config lastet. log_interval: {self.log_interval}s")
        except Exception as e:
            self.status_logger.error(f"Feil ved lasting av averaging config: {e}")

    def start_logging_loop(self):
        threading.Thread(target=self._logging_loop, daemon=True).start()

    def _logging_loop(self):
        while True:
            now = datetime.now()
            if self.logging_enabled:
                data = self.read_all()
                self.save_latest(data)
                self.update_buffer(data)
            if now.hour != self.last_hour:
                self.calculate_hourly_averages()
                self.last_hour = now.hour
            time.sleep(self.log_interval)

    def update_buffer(self, data):
        now = datetime.now()
        for sensor_id, values in data.items():
            entry = {
                "temperature": values["temperature"],
                "humidity": values["humidity"],
                "pressure": values["pressure"],
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
            }
            self.buffer.setdefault(sensor_id, []).append(entry)

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
                json.dump(data, f, indent=2)
            self.status_logger.debug(f"Lagret siste sensorverdier til {self.status_file}")
        except Exception as e:
            self.status_logger.error(f"Feil ved skriving av sensorstatus: {e}")

    def set_logging_enabled(self, enabled: bool):
        self.logging_enabled = enabled
        self.status_logger.info(f"Logging {'aktivert' if enabled else 'deaktivert'}")

    def is_logging_enabled(self):
        return self.logging_enabled

    def set_log_interval(self, seconds: int):
        self.log_interval = seconds
        self.status_logger.info(f"Oppdatert loggeintervall til {seconds} sekunder")

    def calculate_hourly_averages(self):
        now = datetime.now()
        hour_summary = []
        for sensor_id, samples in self.buffer.items():
            if not samples:
                continue
            avg_temp = sum(s["temperature"] for s in samples) / len(samples)
            avg_hum = sum(s["humidity"] for s in samples) / len(samples)
            avg_press = sum(s["pressure"] for s in samples) / len(samples)
            day_period = "natt"
            day_start = datetime.strptime(self.day_start, "%H:%M").time()
            day_end = datetime.strptime(self.day_end, "%H:%M").time()
            if day_start <= now.time() < day_end:
                day_period = "dag"
            entry = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "sensor": sensor_id,
                "avg_temperature": round(avg_temp, 2),
                "avg_humidity": round(avg_hum, 2),
                "avg_pressure": round(avg_press, 2),
                "periode": day_period
            }
            hour_summary.append(entry)
            self.buffer[sensor_id] = []

        try:
            os.makedirs(os.path.dirname(self.averages_file), exist_ok=True)
            with open(self.averages_file, "a") as f:
                for item in hour_summary:
                    f.write(json.dumps(item) + "\n")
            self.status_logger.info(f"Lagret timelig snitt for {len(hour_summary)} sensorer")
        except Exception as e:
            self.status_logger.error(f"Feil ved skriving av snitt: {e}")
