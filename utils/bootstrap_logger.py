# utils/bootstrap_logger.py
import logging, os, datetime

from utils.log_utils import log_event
from config import config_paths as paths



LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, "bootstrap.log")

bootstrap_logger = logging.getLogger("bootstrap")
bootstrap_logger.setLevel(logging.DEBUG)

# File handler
fh = logging.FileHandler(log_file)
fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
bootstrap_logger.addHandler(fh)

# Console handler
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
bootstrap_logger.addHandler(ch)

bootstrap_logger.propagate = False

def log_to_bootstrap(msg):
    log_event(paths.BOOTSTRAP_LOG, msg)
