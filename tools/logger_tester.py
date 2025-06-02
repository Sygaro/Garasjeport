# Fil: tools/logger_tester.py

import time
from utils.logging.unified_logger import get_logger

def test_loggers():
    loggers = {
        "system": get_logger("logger_tester", "system"),
        "test123": get_logger("logger_tester", "testing_123"),
        "port_status": get_logger("logger_tester", "port_status"),
        "garage_controller": get_logger("logger_tester", "garage_controller"),
        "environment": get_logger("logger_tester", "environment"),
    }

    count = 0
    while True:
        for category, logger in loggers.items():
            logger.debug(f"[{category}] DEBUG melding {count}")
            logger.info(f"[{category}] INFO melding {count}")
            logger.warning(f"[{category}] WARNING melding {count}")
            logger.error(f"[{category}] ERROR melding {count}")
        count += 1
        time.sleep(5)

if __name__ == "__main__":
    test_loggers()
