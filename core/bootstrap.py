import os
import json
import shutil
import subprocess
import time
from datetime import datetime
from utils.config_loader import load_config
from utils.version_utils import get_git_version
from utils.bootstrap_logger import bootstrap_logger as logger
from config import config_paths as paths
from utils.file_utils import ensure_directory_exists


status_path = paths.BOOTSTRAP_STATUS_PATH


def validate_json_file(path, description=""):
    if not os.path.exists(path):
        logger.log_error("bootstrap", f"{description} mangler: {path}")
        raise FileNotFoundError(f"{description} mangler: {path}")
    try:
        with open(path, "r") as f:
            json.load(f)
    except json.JSONDecodeError:
        logger.log_error("bootstrap", f"{description} er ikke gyldig JSON: {path}")
        raise


def ensure_required_directories():
    for directory in [
        paths.LOG_DIR,
        paths.ARCHIVE_DIR,
        paths.CONFIG_DIR,
        paths.BACKUP_DIR,
        paths.STATIC_DIR,
        paths.TEMPLATE_DIR,
        paths.DOCS_DIR
    ]:
        ensure_directory_exists(directory)
        logger.log_status("bootstrap", f"Verifisert mappe: {directory}")


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
            logger.log_status("bootstrap", f"Tok sikkerhetskopi av {description} til {backup_path}")


def ensure_pigpiod_running():
    try:
        subprocess.check_output(["pgrep", "pigpiod"])
        logger.log_status("bootstrap", "pigpiod er allerede kjørende")
        return
    except subprocess.CalledProcessError:
        logger.log_warning("pigpiod er ikke startet – prøver å starte...")

    subprocess.run(["pigpiod"])
    time.sleep(1)

    try:
        subprocess.check_output(["pgrep", "pigpiod"])
        logger.log_status("bootstrap", "pigpiod startet OK")
    except subprocess.CalledProcessError:
        logger.log_error("bootstrap", "FEIL: pigpiod kunne ikke startes – systemet vil sannsynligvis feile")


def log_version_info():
    try:
        with open(paths.CONFIG_SYSTEM_PATH, "r") as f:
            system_config = json.load(f)
        version = system_config.get("version", "ukjent")
        logger.log_status("bootstrap", f"Starter system – versjon: {version}")
    except Exception:
        logger.log_warning("Kunne ikke lese versjon fra systemkonfig")


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

    with open(paths.BOOTSTRAP_STATUS_PATH, "w") as f:
        json.dump(status_data, f, indent=2)
    logger.log_status("bootstrap", f"Skrev status til {status_path}")

def log_version_info():
    version = get_git_version()
    logger.log_status("bootstrap", f"Starter system – versjon: {version}")

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

def initialize_system_environment():
    logger.log_status("bootstrap", "Starter systeminitialisering")
    ensure_required_directories()
    ensure_required_config_files()
    ensure_pigpiod_running()
    config_gpio = load_config(paths.CONFIG_GPIO_PATH)
    validate_gpio_config(config_gpio)
    print("[DEBUG] GPIO-config ved validering:")
    print(json.dumps(config_gpio, indent=2))
    log_version_info()
    write_bootstrap_status_file()
    logger.log_status("bootstrap", "Systeminitialisering fullført")
