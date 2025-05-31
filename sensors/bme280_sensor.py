import time
from datetime import datetime
import smbus2
from bme280 import load_calibration_params, sample
from utils.logging.unified_logger import get_logger


#logger = get_logger("sensor_bme280", category="bootstrap")
logger = get_logger("bme280_sensor", category="environment")


class BME280Sensor:
    def __init__(self, sensor_config):
        self.id = sensor_config["id"]
        self.address = int(sensor_config["address"], 16)
        self.bus_number = sensor_config["i2c_bus"]
        self.interval_sec = sensor_config["interval_sec"]
        self.last_read_time = 0

        self.temperature_offset = sensor_config.get("temperature_offset", 0.0)
        self.humidity_offset = sensor_config.get("humidity_offset", 0.0)
        self.altitude = sensor_config.get("altitude", 0.0)

        try:
            self.bus = smbus2.SMBus(self.bus_number)
            self.calibration_params = load_calibration_params(self.bus, self.address)
            logger.debug(f"{self.id}: BME280Sensor initialisert @ 0x{self.address:02X} på bus {self.bus_number}")
        except Exception as e:
            logger.error(f"{self.id}: Klarte ikke å initialisere BME280: {e}")
            raise

    def read_data(self):
        now = time.time()
        if now - self.last_read_time < self.interval_sec:
            return None

        try:
            data = sample(self.bus, self.address, self.calibration_params)

            raw_temp = data.temperature
            raw_hum = data.humidity
            raw_press = data.pressure

            temperature = round(raw_temp + self.temperature_offset, 2)
            humidity = round(raw_hum + self.humidity_offset, 2)

            # Juster trykk for høyde (valgfritt)
            if self.altitude:
                pressure = round(raw_press / pow(1.0 - self.altitude / 44330.0, 5.255), 2)
            else:
                pressure = round(raw_press, 2)

            result = {
                "temperature": temperature,
                "humidity": humidity,
                "pressure": pressure
                #"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.last_read_time = now
            logger.debug(f"{self.id}: Sensorverdier: {result}")
            return result
        except Exception as e:
            logger.error(f"{self.id}: Feil ved lesing fra BME280: {e}")
            return None