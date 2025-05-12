# Fil: logger.py
# Logger for systemhendelser og feil (med fil- og konsollstøtte)

import logging, json, os
from logging.handlers import TimedRotatingFileHandler

def setup_logging(level=logging.INFO):
    os.makedirs("logs", exist_ok=True)

    log_file = "logs/garage.log"  # Endret for å matche resten av appen
    handler = TimedRotatingFileHandler(log_file, when="midnight", backupCount=7, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)  # bruker parameter her!
    root_logger.addHandler(handler)
    root_logger.addHandler(logging.StreamHandler())


try:
        with open("config.json", "r", encoding="utf-8") as f:
            conf = json.load(f)
            level = getattr(logging, conf.get("logging", {}).get("level", "INFO"))
            rotate_days = conf.get("logging", {}).get("rotate_days", 7)
except Exception:
    level = logging.INFO
    rotate_days = 7

    handler = TimedRotatingFileHandler(log_file, when="midnight", backupCount=rotate_days, encoding="utf-8")

try:
        with open("config.json", "r", encoding="utf-8") as f:
            conf = json.load(f)
            level = getattr(logging, conf.get("logging", {}).get("level", "INFO"))
            rotate_days = conf.get("logging", {}).get("rotate_days", 7)
except Exception:
    level = logging.INFO
    rotate_days = 7

    handler = TimedRotatingFileHandler(log_file, when="midnight", backupCount=rotate_days, encoding="utf-8")
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Fjern eksisterende handlers (unngå dobbel logging ved reload)
    if root_logger.handlers:
        for h in root_logger.handlers[:]:
            root_logger.removeHandler(h)

    # Legg til fil og terminalhandler
    root_logger.addHandler(handler)
    root_logger.addHandler(logging.StreamHandler())

    logging.info("🟢 Logging startet")
