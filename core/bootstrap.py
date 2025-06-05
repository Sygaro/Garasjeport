import os
import json
import shutil
import subprocess
import time
from datetime import datetime
from monitor.system_monitor_task import get_system_status, check_thresholds_and_log
from utils.config_loader import load_config
from utils.version_utils import get_git_version
from utils.logging.unified_logger import get_logger
from config import config_paths as paths
from utils.file_utils import ensure_directory_exists
from utils.bootstrap_logger import bootstrap_logger



status_path = paths.STATUS_BOOTSTRAP_PATH
logger = get_logger("bootstrap", category="bootstrap")

# bootstrap_logger.log_status("Starter bootstrap prosess...")
#try:
 #   validate_logging_config()
    #bootstrap_logger.log_status("Logging-konfigurasjon validert")
#except Exception as e:
    #bootstrap_logger.log_error(f"Feil ved validering av logging-konfig: {e}")



def validate_json_file(path, description=""):
    if not os.path.exists(path):
        logger.error(f"{description} mangler: {path}")
        raise FileNotFoundError(f"{description} mangler: {path}")
    try:
        with open(path, "r") as f:
            json.load(f)
    except json.JSONDecodeError:
        logger.error(f"{description} er ikke gyldig JSON: {path}")
        raise


def ensure_required_directories():
    for directory in [
        paths.LOG_DIR,
        paths.ARCHIVE_DIR,
        paths.CONFIG_DIR,
        paths.BACKUP_DIR,
        #paths.STATIC_DIR,
        #paths.TEMPLATE_DIR,
        paths.DOCS_DIR
    ]:
        ensure_directory_exists(directory)
        logger.info(f"Verifisert mappe: {directory}")


def ensure_required_config_files():
    config_files = {
        paths.CONFIG_GPIO_PATH: "GPIO-konfig",
        paths.CONFIG_SYSTEM_PATH: "System-konfig",
        paths.CONFIG_AUTH_PATH: "Autentisering",
        paths.CONFIG_LOGGING_PATH: "Logging-konfig",
        paths.CONFIG_PORTLOGIC_PATH: "Portlogikk-konfig"
    }

    for file_path, description in config_files.items():
        validate_json_file(file_path, description)

        # Backup hvis første gang (ingen kopi finnes)
        backup_path = os.path.join(paths.BACKUP_DIR, os.path.basename(file_path))
        if not os.path.exists(backup_path):
            shutil.copy(file_path, backup_path)
            logger.info(f"Tok sikkerhetskopi av {description} til {backup_path}")


def ensure_pigpiod_running():
    try:
        subprocess.check_output(["pgrep", "pigpiod"])
        logger.info("pigpiod er allerede kjørende")
        return
    except subprocess.CalledProcessError:
        logger.warning("pigpiod er ikke startet – prøver å starte...")

    subprocess.run(["pigpiod"])
    time.sleep(1)

    try:
        subprocess.check_output(["pgrep", "pigpiod"])
        logger.info("pigpiod startet OK")
    except subprocess.CalledProcessError:
        logger.error("FEIL: pigpiod kunne ikke startes – systemet vil sannsynligvis feile")


def log_version_info():
    version = get_git_version()
    logger.info(f"Starter system – versjon: {version}")
    try:
        with open(paths.CONFIG_SYSTEM_PATH, "r") as f:
            system_config = json.load(f)
        version = system_config.get("version", "ukjent")
        logger.info(f"Starter system – versjon: {version}")
    except Exception:
        logger.warning("Kunne ikke lese versjon fra systemkonfig")


def write_bootstrap_status_file():
    os.makedirs(paths.STATUS_DIR, exist_ok=True)
    status_data = {
        "bootstrap_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pigpiod_expected": True,
        "config_validated": True,
        "version": None
    }
    try:
        with open(paths.CONFIG_SYSTEM_PATH, "r") as f:
            config = json.load(f)
            from utils.version_utils import get_git_version
            status_data["version"] = get_git_version()
    except:
        status_data["version"] = "ukjent"
        status_data["config_validated"] = False

    with open(paths.STATUS_BOOTSTRAP_PATH, "w") as f:
        json.dump(status_data, f, indent=2)
    logger.info(f"Skrev status til {status_path}")
    

def validate_gpio_config(config_gpio):
    from utils.bootstrap_logger import log_to_bootstrap

    if not config_gpio:
        raise ValueError("Ingen GPIO-konfigurasjon funnet eller filen er tom.")

    sensor_pins = config_gpio.get("sensor_pins")
    if not isinstance(sensor_pins, dict):
        raise ValueError("sensor_pins mangler eller er feil format i config_gpio.json")

    errors = []
    for port, sensors in sensor_pins.items():
        if "open" not in sensors:
            errors.append(f"Port '{port}' mangler 'open'-sensor")
        if "closed" not in sensors:
            errors.append(f"Port '{port}' mangler 'closed'-sensor")

    if errors:
        for err in errors:
            log_to_bootstrap(f"[ERROR] Konfigurasjonsfeil: {err}")
        raise ValueError("Ugyldig sensorspesifikasjon i config_gpio.json")
    
def validate_config_timing(config):
    """
    Validerer innholdet i config_timing.json for nødvendige felter og typer.
    Kaster ValueError eller TypeError ved feil.
    """
    required_fields = {
        "default_open_time": (int, float),
        "default_close_time": (int, float),
        "fail_margin_status_change": int,
        "t0_max_delay": (int, float),
        "timing_history_size": int
    }

    timing = config.get("timing_config")
    if not timing:
        raise ValueError("timing_config mangler i config_timing.json")

    for key, expected_type in required_fields.items():
        value = timing.get(key)
        if value is None:
            raise ValueError(f"{key} mangler i timing_config")
        if not isinstance(value, expected_type):
            raise TypeError(f"{key} må være av type {expected_type}, men fikk {type(value)}")

    return True

def validate_config_system(config):
    """
    Validerer innholdet i config_system.json for hver port og alarm_config.
    """
    if not isinstance(config, dict):
        raise ValueError("config_system må være et dictionary")

    # Valider per port (eks: "port1", "port2")
    for port, data in config.items():
        if port == "alarm_config":
            continue  # valideres senere

        if not isinstance(data, dict):
            raise ValueError(f"{port} må være en dictionary")

        if "status" not in data or not isinstance(data["status"], str):
            raise ValueError(f"{port}: status mangler eller er ikke en streng")

        if "status_timestamp" in data and not isinstance(data["status_timestamp"], str):
            raise TypeError(f"{port}: status_timestamp må være en streng hvis den finnes")

        # Valider timing-delen
        timing = data.get("timing", {})
        for direction in ["open", "close"]:
            dir_data = timing.get(direction, {})
            if not isinstance(dir_data, dict):
                continue  # tillat at det mangler før første måling

            for key in ["last", "avg", "t0", "t1", "t2"]:
                val = dir_data.get(key)
                if val is not None and not isinstance(val, (int, float)):
                    raise TypeError(f"{port}: timing.{direction}.{key} må være tall")

            history = dir_data.get("history", [])
            if not isinstance(history, list):
                raise TypeError(f"{port}: timing.{direction}.history må være en liste")
            if not all(isinstance(h, (int, float)) for h in history):
                raise TypeError(f"{port}: timing.{direction}.history inneholder ikke bare tall")

        # Valider alarm_state
        alarm = data.get("alarm_state", {})
        if alarm:
            if "active" in alarm and not isinstance(alarm["active"], bool):
                raise TypeError(f"{port}: alarm_state.active må være bool")
            if "last_triggered" in alarm and alarm["last_triggered"] is not None and not isinstance(alarm["last_triggered"], str):
                raise TypeError(f"{port}: alarm_state.last_triggered må være en streng eller null")
            if "retries_left" in alarm and not isinstance(alarm["retries_left"], int):
                raise TypeError(f"{port}: alarm_state.retries_left må være int")

    # Valider global alarm_config
    alarm_config = config.get("alarm_config")
    if not alarm_config:
        raise ValueError("alarm_config mangler i config_system.json")

    expected_alarm_fields = {
        "enabled": bool,
        "trigger_after_minutes": int,
        "repeat_interval_minutes": int,
        "max_retries": int
    }

    for key, expected_type in expected_alarm_fields.items():
        value = alarm_config.get(key)
        if value is None:
            raise ValueError(f"alarm_config.{key} mangler")
        if not isinstance(value, expected_type):
            raise TypeError(f"alarm_config.{key} må være av type {expected_type.__name__}")

    return True

def validate_config_health(config):
    """
    Validerer strukturen og verdiene i config_health.json
    Krever at nødvendige thresholds og alerts finnes og har korrekt type.
    """

    # Valider thresholds
    required_thresholds = {
        "cpu_temp_max": (int, float),
        "disk_usage_max_percent": int,
        "memory_usage_max_percent": int,
        "min_free_disk_gb": (int, float),
        "min_free_memory_mb": int,
        "update_warning_threshold": int
    }

    thresholds = config.get("thresholds")
    if not thresholds or not isinstance(thresholds, dict):
        raise ValueError("Mangler eller ugyldig 'thresholds' blokk i config_health.json")

    for key, expected_type in required_thresholds.items():
        value = thresholds.get(key)
        if value is None:
            raise ValueError(f"Mangler terskel: thresholds.{key}")
        if not isinstance(value, expected_type):
            raise ValueError(f"Ugyldig type for thresholds.{key}: forventet {expected_type}, fikk {type(value)}")

    # Valider alerts
    alerts = config.get("alerts")
    if not alerts or not isinstance(alerts, dict):
        raise ValueError("Mangler eller ugyldig 'alerts' blokk i config_health.json")

    if "enabled" not in alerts:
        raise ValueError("Mangler 'alerts.enabled'")

    if not isinstance(alerts["enabled"], bool):
        raise ValueError("'alerts.enabled' må være en bool")

    if "repeat_interval_min" in alerts and not isinstance(alerts["repeat_interval_min"], int):
        raise ValueError("'alerts.repeat_interval_min' må være int hvis definert")

    if "max_repeats" in alerts and not isinstance(alerts["max_repeats"], int):
        raise ValueError("'alerts.max_repeats' må være int hvis definert")

    return True


def initialize_system_environment():
    logger.info("Starter systeminitialisering")
    ensure_required_directories()
    ensure_required_config_files()
    ensure_pigpiod_running()
    config_gpio = load_config(paths.CONFIG_GPIO_PATH)
    validate_gpio_config(config_gpio)
    try:
        config_timing = load_config(paths.CONFIG_TIMING_PATH)
        validate_config_timing(config_timing)
        logger.info("config_timing.json validert OK")
    except Exception as e:
        logger.error(f"Feil ved validering av config_timing.json: {e}")
        raise
    
    try:
        config_system = load_config(paths.CONFIG_SYSTEM_PATH)
        validate_config_system(config_system)
        logger.info("config_system.json validert OK")
    except Exception as e:
        logger.error(f"Feil ved validering av config_system.json: {e}")
        raise
    try:
        config_health = load_config(paths.CONFIG_HEALTH_PATH)
        validate_config_health(config_health)
        logger.info("config_health.json validert OK")
    except Exception as e:
        logger.error(f"Validering av config_health.json feilet: {e}")
        raise
    log_version_info()
    write_bootstrap_status_file()
    logger.info("Systeminitialisering fullført")

    status = get_system_status()
    check_thresholds_and_log(status)
    logger.debug(f"Systemstatus ved oppstart: {status}")
