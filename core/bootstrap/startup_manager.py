from core.bootstrap.logger_initializer import setup_logger, shutdown_bootstrap_logger
from core.bootstrap.config_validator import validate_config_paths
from config import config_paths
import os
import sys
import json
from datetime import datetime

def write_bootstrap_status(status: str, details: str):
    """Skriv statusrapport til STATUS_BOOTSTRAP_PATH"""
    try:
        config_paths.STATUS_BOOTSTRAP_PATH.parent.mkdir(parents=True, exist_ok=True)
        status_data = {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        with open(config_paths.STATUS_BOOTSTRAP_PATH, "w") as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        print(f"[BOOTSTRAP STATUS FEIL] Kunne ikke skrive status: {e}")

def check_directories(directories, logger):
    success = True
    for dir_path in directories:
        if not dir_path.exists():
            try:
                os.makedirs(dir_path)
                logger.info(f"Opprettet manglende katalog: {dir_path}")
            except Exception as e:
                logger.critical(f"Kunne ikke opprette katalog '{dir_path}': {str(e)}")
                success = False
    return success

def run_bootstrap():
    logger = setup_logger()
    logger.info("=== Starter bootstrap ===")

    logger.info("Validerer konfigurasjonsfiler...")
    if not validate_config_paths(logger):
        error_msg = "Konfigurasjonsvalidering feilet."
        logger.critical(error_msg)
        write_bootstrap_status("error", error_msg)
        shutdown_bootstrap_logger()
        sys.exit(1)

    logger.info("Sjekker systemkataloger...")
    required_dirs = [config_paths.LOG_BOOTSTRAP_PATH.parent, config_paths.CONFIG_BOOTSTRAP_PATH.parent]
    optional_dirs = [config_paths.STATUS_BOOTSTRAP_PATH.parent]

    if not check_directories(required_dirs, logger):
        error_msg = "Kritiske kataloger kunne ikke opprettes."
        logger.critical(error_msg)
        write_bootstrap_status("error", error_msg)
        shutdown_bootstrap_logger()
        sys.exit(1)

    check_directories(optional_dirs, logger)

    logger.info("Bootstrap fullført uten kritiske feil.")
    write_bootstrap_status("ok", "Bootstrap fullført")
    shutdown_bootstrap_logger()
