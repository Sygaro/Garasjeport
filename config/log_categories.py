# config/log_categories.py

#from typing import FrozenSet
from config import config_paths


"""
log_categories.py
Inneholder en definert liste over gyldige loggkategorier brukt i hele systemet.
Denne listen brukes til validering, konfigurering og ruting av logger.
"""


LOG_CATEGORIES: dict[str, str] = {
    "port_activity": config_paths.LOG_ACTIVITY_PATH,
    "port_status": config_paths.LOG_STATUS_PATH,
    "port_timing": config_paths.LOG_TIMING_PATH,
    "bootstrap": config_paths.LOG_BOOTSTRAP_PATH,
    "garage_controller": config_paths.LOG_GARAGE_CONTROLLER_PATH,
    "environment": config_paths.LOG_SENSOR_ENV_PATH,
    "api": config_paths.LOG_API_PATH,
    "system": config_paths.LOG_SYSTEM_PATH,
    "unknown_category": config_paths.LOG_UNKNOWN_CATEGORY_PATH #"Logger for ugyldige eller udefinerte kategorier"
}


def is_valid_category(category: str) -> bool:
    return category in LOG_CATEGORIES

