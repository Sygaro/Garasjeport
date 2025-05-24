import subprocess, datetime, json, os
 

from utils.bootstrap_logger import log_to_bootstrap
from utils.file_utils import load_json, save_json
from utils.system_utils import check_or_start_pigpiod
from config.config_paths import (
    CONFIG_DIR,
    CONFIG_GPIO_PATH,
    CONFIG_SYSTEM_PATH,
    CONFIG_AUTH_PATH,
    CONFIG_LOGGING_PATH,
    LOG_DIR,
    BACKUP_DIR,
    DOCS_DIR
)
from utils.bootstrap_logger import bootstrap_logger as logger


def ensure_directories():
    for path in [LOG_DIR, CONFIG_DIR, BACKUP_DIR, DOCS_DIR]:
        os.makedirs(path, exist_ok=True)
        logger.info(f"Kontrollerte mappe: {path}")


def ensure_config_files():
    if not os.path.exists(CONFIG_GPIO_PATH):
        logger.warning("Mangler config_gpio.json - oppretter standard")
        save_json(CONFIG_GPIO_PATH, {
            "relay_pins": {
                "port1": 14,
                "port2": 15
            },
            "sensor_pins": {
                "port1": {"open": 23, "closed": 24},
                "port2": {"open": 20, "closed": 21}
            },
            "relay_config": {
                "pulse_duration": 0.5,
                "active_state": 0,
                "fail_margin_status_change": 5,
                "port_status_change_timeout": 60
            },
            "sensor_config": {
                "pull": "up",
                "active_state": 0
            }
        })

    if not os.path.exists(CONFIG_SYSTEM_PATH):
        logger.warning("Mangler config_system.json - oppretter standard")
        save_json(CONFIG_SYSTEM_PATH, {"timing": {}})

    if not os.path.exists(CONFIG_AUTH_PATH):
        logger.warning("Mangler config_auth.json - oppretter standard")
        save_json(CONFIG_AUTH_PATH, {"api_token": "changeme"})

    if not os.path.exists(CONFIG_LOGGING_PATH):
        logger.warning("Mangler config_logging.json - oppretter standard")
        save_json(CONFIG_LOGGING_PATH, {})


def validate_config_gpio():
    path = os.path.join(CONFIG_DIR, "config_gpio.json")
    try:
        with open(path) as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"[BOOTSTRAP] Feil ved lesing av config_gpio.json: {e}")
        raise SystemExit("[BOOTSTRAP] Avslutter pga. konfigurasjonsfeil.")

    errors = []

    # Valider rele-pinner og sensor-pinner
    relay_pins = config.get("relay_pins", {})
    sensor_pins = config.get("sensor_pins", {})

    for port in ["port1", "port2"]:
        if port not in relay_pins:
            errors.append(f"Mangler relay_pins['{port}']")
        if port not in sensor_pins:
            errors.append(f"Mangler sensor_pins['{port}']")
        else:
            for s in ["open", "closed"]:
                if s not in sensor_pins[port]:
                    errors.append(f"Mangler sensor_pins['{port}']['{s}']")

    # ✅ Valider relay_config
    relay_conf = config.get("relay_config", {})
    for key in ["active_state", "pulse_duration", "max_sensor_start_delay"]:
        if key not in relay_conf:
            errors.append(f"Mangler relay_config.{key}")

    # ✅ Valider timing_config
    timing_conf = config.get("timing_config", {})
    for key in ["fast_poll_interval", "slow_poll_interval", "port_status_change_timeout", "fail_margin_status_change"]:
        if key not in timing_conf:
            errors.append(f"Mangler timing_config.{key}")

    if errors:
        print("[BOOTSTRAP] FEIL i GPIO-konfig:")
        for err in errors:
            print("  ⚠️", err)
        raise SystemExit("[BOOTSTRAP] Avslutter pga. GPIO-konfigfeil.")
    else:
        logger.info("[BOOTSTRAP] config_gpio.json validering OK")


def validate_config_system():
    try:
        config = load_json(CONFIG_SYSTEM_PATH)
        timing = config.get("timing", {})

        for port, data in timing.items():
            for key in ["open_time", "close_time", "open_timestamp", "close_timestamp"]:
                if key not in data:
                    logger.warning(f"Mangler '{key}' for {port} i config_system.json")

    except Exception as e:
        logger.error(f"Klarte ikke å validere config_system.json: {e}")
        raise SystemExit("[BOOTSTRAP] Avslutter pga. config-systemfeil.")


def initialize_system_environment():
    print("[BOOTSTRAP] Initialiserer systemmiljø...")
    check_or_start_pigpiod()
    logger.info("Starter miljøinitialisering...")
    ensure_directories()
    ensure_config_files()
    validate_config_gpio()
    validate_config_system()
    logger.info("Systemmiljø er klart.")
