# ==========================================
# Filnavn: bootstrap.py
# Initierer loggmappene, loggfiler, config og backups
# ==========================================

## core/bootstrap.py

import os
import json
import logging
from datetime import datetime
from config.config_paths import LOG_DIR, CONFIG_DIR, BACKUP_DIR, DOCS_DIR, CONFIG_SYSTEM_PATH
from config.default_config import DEFAULT_CONFIGS, REQUIRED_LOG_FILES
from utils.file_utils import load_json, save_json


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
    Validerer at config_gpio.json inneholder gyldig struktur og unike GPIO-pinner.
    Logger advarsler for manglende felt og stopper ved alvorlige feil.
    """
    path = os.path.join(CONFIG_DIR, "config_gpio.json")
    try:
        with open(path) as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"[BOOTSTRAP] Feil ved lesing av config_gpio.json: {e}")
        raise SystemExit("[BOOTSTRAP] Avslutter pga. feil under konfigvalidering.")

    relay_pins = config.get("relay_pins", {})
    sensor_pins = config.get("sensor_pins", {})

    # 🔍 Sanity check for manglende felter
    for port in ["port1", "port2"]:
        if port not in relay_pins:
            logger.warning(f"[BOOTSTRAP] Mangler relay_pin for {port}")
        if port not in sensor_pins:
            logger.warning(f"[BOOTSTRAP] Mangler sensor_pins for {port}")
        else:
            for s in ["open", "closed"]:
                if s not in sensor_pins[port]:
                    logger.warning(f"[BOOTSTRAP] Mangler sensor_pins['{port}']['{s}']")

    # 🔐 Valider at pinner er heltall og unike
    used = set()
    errors = []

    for pin in relay_pins.values():
        if not isinstance(pin, int) or pin in used:
            errors.append(f"Ugyldig eller duplikat rele-pin: {pin}")
        used.add(pin)

    for port, sensors in sensor_pins.items():
        for name, pin in sensors.items():
            if not isinstance(pin, int) or pin in used:
                errors.append(f"Ugyldig eller duplikat sensor-pin: {pin} ({port}/{name})")
            used.add(pin)

    if errors:
        print("[BOOTSTRAP] FEIL i GPIO-konfig:")
        for err in errors:
            print("  ⚠️", err)
        raise SystemExit("[BOOTSTRAP] Avslutter pga. GPIO-konfigfeil.")


def initialize_system_environment():
    logger.info("Starter miljøinitialisering...")
    ensure_directories()
    ensure_config_files()
    ensure_log_files()
    validate_config_gpio()
    logger.info("Systemmiljø er klart.")
    try:
        config = load_json(CONFIG_SYSTEM_PATH)

        # Opprett standard timing-felt hvis mangler
        if "port_timings" not in config:
            config["port_timings"] = {
                "port1": {"open_time": 60, "close_time": 60, "timestamp": None},
                "port2": {"open_time": 60, "close_time": 60, "timestamp": None}
            }
            save_json(CONFIG_SYSTEM_PATH, config)
            print("[BOOTSTRAP] Lagt til manglende 'port_timings' i config_system.json")
    except Exception as e:
        print(f"[BOOTSTRAP] Klarte ikke å validere config_system.json: {e}")
        raise SystemExit("[BOOTSTRAP] Avslutter pga. config-systemfeil.")

    logger.info("Systemmiljø er klart.")
