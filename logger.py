# Fil: logger.py
# Logger for systemhendelser og feil

import logging
from logging.handlers import TimedRotatingFileHandler
import os


# Konfigurer logging én gang
logging.basicConfig(
    filename="system.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_event(message: str):
    logging.info(message)


def setup_logging():
    os.makedirs("logs", exist_ok=True)
    log_file = "logs/system.log"
    handler = TimedRotatingFileHandler(log_file, when="midnight", backupCount=7)
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
    root_logger.addHandler(logging.StreamHandler())  # Log til terminal også
