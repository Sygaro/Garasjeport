
# Fil: calibration_logger.py
# Logger kalibreringsmålinger til en separat loggfil (JSONL-format)

import json
from datetime import datetime
import os

LOG_FILE = "logs/calibration_history.log"

def log_calibration_result(port, direction, rele_delay, sensor_to_sensor, total_time, temp=None, humidity=None):
    entry = {
        "time": datetime.now().isoformat(),
        "port": port,
        "type": direction,  # "open" eller "close"
        "rele_delay": round(rele_delay, 3),
        "sensor_to_sensor": round(sensor_to_sensor, 3),
        "total_time": round(total_time, 3),
        "temp": temp,
        "humidity": humidity
    }

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
