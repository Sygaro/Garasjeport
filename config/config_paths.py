# config_paths.py

"""
Definerer globale stier til viktige mapper i prosjektet.
Bruk disse i stedet for å hardkode "logs/", "config/" osv. i resten av koden.
"""

import os

# Grunnsti (rotmappe)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# === Kataloger ===
LOG_DIR = os.path.join(BASE_DIR, "logs")
ARCHIVE_DIR = os.path.join(LOG_DIR, "archived")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
STATUS_DIR = os.path.join(BASE_DIR, "status")
#STATIC_DIR = os.path.join(BASE_DIR, "static")
#TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
DATA_DIR = os.path.join(BASE_DIR, "data")


# === Konfigurasjonsfiler ===
CONFIG_GPIO_PATH = os.path.join(CONFIG_DIR, "config_gpio.json")
CONFIG_SYSTEM_PATH = os.path.join(CONFIG_DIR, "config_system.json")
CONFIG_AUTH_PATH = os.path.join(CONFIG_DIR, "config_auth.json")
CONFIG_LOGGING_PATH = os.path.join(CONFIG_DIR, "config_logging.json")
CONFIG_PORTLOGIC_PATH = os.path.join(CONFIG_DIR, "config_portlogic.json")
CONFIG_TIMING_PATH = os.path.join(CONFIG_DIR, "config_timing.json")
CONFIG_HEALTH_PATH = os.path.join(CONFIG_DIR, "config_health.json")
CONFIG_SENSOR_ENV_PATH = os.path.join(CONFIG_DIR, "config_sensors_env.json")


# API og datafiler
ACCESS_TOKENS_PATH = os.path.join(DATA_DIR, "access_tokens.json")
ACCESS_SESSION_LOG_PATH = os.path.join(DATA_DIR, "access_session_log.json")


# === Loggfiler ===
LOG_STATUS_PATH = os.path.join(LOG_DIR, "status.log")
LOG_ERROR_PATH = os.path.join(LOG_DIR, "errors.log")
LOG_ACTIVITY_PATH = os.path.join(LOG_DIR, "activity.log")
LOG_TIMING_PATH = os.path.join(LOG_DIR, "timing.log")
LOG_BOOTSTRAP_PATH = os.path.join(LOG_DIR, "bootstrap.log")
LOG_SENSOR_ENV_AVERAGES_PATH = os.path.join(LOG_DIR, "sensor_env_averages.log")
LOG_SENSOR_ENV_PATH = os.path.join(LOG_DIR, "environment.log")
LOG_GARAGE_CONTROLLER_PATH = os.path.join(LOG_DIR, "garage_controller.log")
LOG_SYSTEM_PATH = os.path.join(LOG_DIR, "system.log")




# === Status- og helsefiler ===
STATUS_PIGPIO_PATH = os.path.join(STATUS_DIR, "pigpio_status.json")
STATUS_BOOTSTRAP_PATH = os.path.join(STATUS_DIR, "bootstrap_status.json")
STATUS_FRONTEND_VERSION_PATH = os.path.join(STATUS_DIR, "frontend_version.json")
STATUS_SENSOR_ENV_PATH = os.path.join(STATUS_DIR, "sensor_env_data.json")


