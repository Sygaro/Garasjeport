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
TEMP_DIR = os.path.join(BASE_DIR, "temp")

# === Konfigurasjonsfiler ===
CONFIG_GPIO_PATH = os.path.join(CONFIG_DIR, "config_gpio.json")
CONFIG_SYSTEM_PATH = os.path.join(CONFIG_DIR, "config_system.json")
CONFIG_AUTH_PATH = os.path.join(CONFIG_DIR, "config_auth.json")
CONFIG_LOGGING_PATH = os.path.join(CONFIG_DIR, "config_logging.json")
CONFIG_PORTLOGIC_PATH = os.path.join(CONFIG_DIR, "config_portlogic.json")
CONFIG_TIMING_PATH = os.path.join(CONFIG_DIR, "config_timing.json")
CONFIG_HEALTH_PATH = os.path.join(CONFIG_DIR, "config_health.json")
CONFIG_SENSOR_ENV_PATH = os.path.join(CONFIG_DIR, "config_sensor_env.json")
CONFIG_BOOTSTRAP_PATH = os.path.join(CONFIG_DIR, "config_bootstrap.json")


# API og datafiler
ACCESS_TOKENS_PATH = os.path.join(DATA_DIR, "access_tokens.json")
ACCESS_SESSION_LOG_PATH = os.path.join(DATA_DIR, "access_session_log.json")


# === Loggfiler ===
LOG_STATUS_PATH = os.path.join(LOG_DIR, "status.log")
LOG_ERROR_PATH = os.path.join(LOG_DIR, "errors.log")
LOG_ACTIVITY_PATH = os.path.join(LOG_DIR, "port_activity.log")
LOG_TIMING_PATH = os.path.join(LOG_DIR, "timing.log")
LOG_BOOTSTRAP_PATH = os.path.join(LOG_DIR, "bootstrap.log")
LOG_SENSOR_ENV_AVERAGES_PATH = os.path.join(LOG_DIR, "sensor_env_averages.json")
LOG_SENSOR_ENV_PATH = os.path.join(LOG_DIR, "environment.log")
LOG_GARAGE_CONTROLLER_PATH = os.path.join(LOG_DIR, "garage_controller.log")
LOG_SYSTEM_PATH = os.path.join(LOG_DIR, "system.log")
LOG_API_PATH= os.path.join(LOG_DIR, "api_system.log")
LOG_UNKNOWN_CATEGORY_PATH = os.path.join(LOG_DIR, "unknown_category.log")
LOG_ENV_MANAGER_PATH = os.path.join(LOG_DIR, "env_manager.log")


# === Status- og helsefiler ===
STATUS_PIGPIO_PATH = os.path.join(STATUS_DIR, "pigpio_status.json")
STATUS_BOOTSTRAP_PATH = os.path.join(STATUS_DIR, "bootstrap_status.json")
STATUS_FRONTEND_VERSION_PATH = os.path.join(STATUS_DIR, "frontend_version.json")
STATUS_SENSOR_ENV_PATH = os.path.join(STATUS_DIR, "sensor_env_data.json")


# === Lister for bootstrap/startup-sjekk av systemet ===

# Kataloger som MÅ finnes før systemet kan startes (bootstrap vil opprette disse hvis de mangler)
REQUIRED_DIRECTORIES = [
    LOG_DIR,       # Hovedkatalog for alle loggfiler
    CONFIG_DIR,    # Katalog for all konfigurasjon (.json-filer)
    STATUS_DIR,    # Katalog for statusfiler (f.eks. bootstrap-status, system-status)
]

# Kataloger som er anbefalt, men ikke kritisk for oppstart (styres via config/bootstrap_logging.json)
OPTIONAL_DIRECTORIES = [
    DATA_DIR,      # Til lagring av runtime-data (API tokens osv.)
    TEMP_DIR,      # Midlertidige arbeidsfiler
    ARCHIVE_DIR,   # For arkiverte/roterte logger eller backup
    BACKUP_DIR,    # Sikkerhetskopier av kritiske configfiler
    DOCS_DIR,      # Dokumentasjon, hjelpesider, API-docs osv.
]

# Konfigurasjonsfiler som er KRITISKE for å starte systemet – med beskrivelse for logging/debugging
REQUIRED_CONFIG_FILES = [
    (CONFIG_GPIO_PATH,         "GPIO-konfig (oppsett av GPIO-pinner for releer og sensorer)"),
    (CONFIG_SYSTEM_PATH,       "System-konfig (generelle systeminnstillinger, navn osv.)"),
    (CONFIG_AUTH_PATH,         "Autentisering (API/admin-brukere og tilgang)"),
    (CONFIG_LOGGING_PATH,      "Logging-konfig (oppsett og struktur for logger)"),
    (CONFIG_PORTLOGIC_PATH,    "Portlogikk-konfig (styringsregler og logikk for porter)"),
    (CONFIG_TIMING_PATH,       "Tidsinnstillinger (impulslengde, timeout, varslingstid etc.)"),
    (CONFIG_HEALTH_PATH,       "Helsemonitor-konfig (grenser og regler for systemovervåking)"),
    (CONFIG_BOOTSTRAP_PATH,    "Bootstrap-konfig (egen config for bootstrap/logger/valgfrie kataloger)"),
    # Legg til flere configfiler her hvis systemet utvides!
]

# Statusfiler som skal sjekkes og opprettes av bootstrap hvis de mangler
REQUIRED_STATUS_FILES = [
    (STATUS_PIGPIO_PATH, "pigpio-status (brukes til å lagre pigpio helsestatus)"),
    (STATUS_BOOTSTRAP_PATH, "bootstrap-status (sist kjørte bootstrap, for API)"),
    (STATUS_FRONTEND_VERSION_PATH, "frontend-versjon (for versjonskontroll mellom backend/frontend)"),
    (STATUS_SENSOR_ENV_PATH, "sensor-miljødata (lagrer siste sensormålinger)"),
    # legg til flere statusfiler her!
]


# Tips:
# - Disse listene gjør bootstrap-koden 100% dynamisk og uten hardkoding.
# - Ved utvidelse: legg til nye (sti, beskrivelse)-tupler i listen.
# - Beskrivelsen brukes i logg og feilmeldinger, og gjør feilsøking enklere.
