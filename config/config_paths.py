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
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

# === Konfigurasjonsfiler ===
CONFIG_GPIO_PATH = os.path.join(CONFIG_DIR, "config_gpio.json")
CONFIG_SYSTEM_PATH = os.path.join(CONFIG_DIR, "config_system.json")
CONFIG_AUTH_PATH = os.path.join(CONFIG_DIR, "config_auth.json")
CONFIG_LOGGING_PATH = os.path.join(CONFIG_DIR, "config_logging.json")
CONFIG_PORTLOGIC_PATH = os.path.join(CONFIG_DIR, "config_portlogic.json")
CONFIG_TIMING_PATH = os.path.join(CONFIG_DIR, "config_timing.json")
CONFIG_HEALTH_PATH = os.path.join(CONFIG_DIR, "config_health.json")



# === Loggfiler ===
STATUS_LOG = os.path.join(LOG_DIR, "status.log")
ERROR_LOG = os.path.join(LOG_DIR, "errors.log")
ACTIVITY_LOG = os.path.join(LOG_DIR, "activity.log")
TIMING_LOG = os.path.join(LOG_DIR, "timing.log")
BOOTSTRAP_LOG = os.path.join(LOG_DIR, "bootstrap.log")


# === Status- og helsefiler ===
PIGPIO_STATUS_PATH = os.path.join(STATUS_DIR, "pigpio_status.json")
BOOTSTRAP_STATUS_PATH = os.path.join(STATUS_DIR, "bootstrap_status.json")

FRONTEND_VERSION_PATH = os.path.join(STATUS_DIR, "frontend_version.json")

# === Sensorsystem ===
CONFIG_SENSORS_PATH = os.path.join(CONFIG_DIR, "config_sensors.json")
SENSOR_STATUS_PATH = os.path.join(STATUS_DIR, "sensor_data.json")
SENSOR_LOG_PATH = os.path.join(LOG_DIR, "sensor_data.log")
SENSOR_AVERAGES_PATH = os.path.join(LOG_DIR, "sensor_averages.log")



