#from utils.logging.unified_logger import get_logger
# utils/bootstrap_logger.py
import os
import logging
# from datetime import datetime
from config import config_paths as paths

logfile_path = paths.LOG_BOOTSTRAP_PATH

# Sørg for at loggmappe eksisterer
os.makedirs(os.path.dirname(logfile_path), exist_ok=True)

logging.basicConfig(
    filename=logfile_path,
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log_to_bootstrap(message: str):
    logging.info(message)

# === Ekstra metoder for strukturert bruk ===

def log_status(context: str, message: str):
    log_to_bootstrap(f"[STATUS] {context}: {message}")

def log_error(context: str, message: str):
    log_to_bootstrap(f"[ERROR] {context}: {message}")

def log_warning(context: str, message: str):
    log_to_bootstrap(f"[WARNING] {context}: {message}")

# === Eksporterbar "logger-lignende" alias hvis ønskelig ===
class BootstrapLogger:
    def log_status(self, context, message):
        log_status(context, message)

    def log_error(self, context, message):
        log_error(context, message)

    def log_warning(self, context, message):
        log_warning(context, message)

bootstrap_logger = BootstrapLogger()
