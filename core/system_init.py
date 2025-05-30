# Fil: core/system_init.py
#from utils.logging.unified_logger import get_logger
from utils.logging.logger_validation import validate_logging_config

# Placeholder for annen initlogikk: GPIO, sensorer, releer osv.
def init():
    validate_logging_config()  # Validér logger-oppsettet tidlig
    # TODO: Initier GPIO, rele, sensorer, etc.
    print("✅ Systeminitiering fullført.")
