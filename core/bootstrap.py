# ==========================================
# Filnavn: bootstrap.py
# Initierer loggmappene, loggfiler, config og backups
# ==========================================

## core/bootstrap.py

import os
import json
import logging
from datetime import datetime
from config.config_paths import LOG_DIR, CONFIG_DIR, BACKUP_DIR, DOCS_DIR
from config.default_config import DEFAULT_CONFIGS, REQUIRED_LOG_FILES

# Opprett logger for bootstrap-prosessen
def setup_bootstrap_logger():
    log_path = os.path.join(LOG_DIR, "system.log")
    logger = logging.getLogger("bootstrap")
    logger.setLevel(logging.INFO)

    # Filhandler
    fh = logging.FileHandler(log_path)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

    # Konsollhandler
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[BOOTSTRAP] %(message)s"))

    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.propagate = False
    return logger

logger = setup_bootstrap_logger()

def ensure_directories():
    for path in [LOG_DIR, CONFIG_DIR, BACKUP_DIR, DOCS_DIR]:
        os.makedirs(path, exist_ok=True)
        logger.info(f"Kontrollerte mappe: {path}")

def ensure_config_files():
    for filename, default_data in DEFAULT_CONFIGS.items():
        path = os.path.join(CONFIG_DIR, filename)
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump(default_data, f, indent=2)
            logger.info(f"Opprettet manglende config-fil: {filename}")

def ensure_log_files():
    for log_file in REQUIRED_LOG_FILES:
        path = os.path.join(LOG_DIR, log_file)
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write(f"# Opprettet {datetime.now().isoformat()}\n")
            logger.info(f"Opprettet loggfil: {log_file}")

def validate_config_gpio():
    """
    Enkel sanity check av struktur i config_gpio.json.
    Logger advarsler ved mangler.
    """
    path = os.path.join(CONFIG_DIR, "config_gpio.json")
    try:
        with open(path) as f:
            config = json.load(f)

        relay_pins = config.get("relay_pins", {})
        sensor_pins = config.get("sensor_pins", {})

        for port in ["port1", "port2"]:
            if port not in relay_pins:
                logger.warning(f"Mangler relay_pin for {port}")
            if port not in sensor_pins:
                logger.warning(f"Mangler sensor_pins for {port}")
            else:
                for s in ["open", "closed"]:
                    if s not in sensor_pins[port]:
                        logger.warning(f"Mangler sensor_pins['{port}']['{s}']")

    except Exception as e:
        logger.error(f"Feil ved lesing av config_gpio.json: {e}")

def initialize_system_environment():
    logger.info("Starter miljøinitialisering...")
    ensure_directories()
    ensure_config_files()
    ensure_log_files()
    validate_config_gpio()
    logger.info("Systemmiljø er klart.")
