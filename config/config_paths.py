# config/config_paths.py

"""
Definerer globale stier til viktige mapper i prosjektet.
Bruk disse i stedet for å hardkode "logs/", "config/" osv. i resten av koden.
"""

import os

# Roterer utgangspunktet til prosjektets rotmappe
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Absolutte stier til kjernemapper
LOG_DIR = os.path.join(BASE_DIR, "logs")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

CONFIG_GPIO_PATH = os.path.join(CONFIG_DIR, "config_gpio.json")
CONFIG_SYSTEM_PATH = os.path.join(CONFIG_DIR, "config_system.json")
CONFIG_AUTH_PATH = os.path.join(CONFIG_DIR, "config_auth.json")
CONFIG_LOGGING_PATH = os.path.join(CONFIG_DIR, "config_logging.json")

STATUS_LOG = os.path.join(LOG_DIR, "status.log")
ERROR_LOG = os.path.join(LOG_DIR, "errors.log")
ACTIVITY_LOG = os.path.join(LOG_DIR, "activity.log")
TIMING_LOG = os.path.join(LOG_DIR, "timing.log")
BOOTSTRAP_LOG = os.path.join(LOG_DIR, "bootstrap.log")
ARCHIVE_DIR = os.path.join(LOG_DIR, "archived")
