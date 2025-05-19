# utils/bootstrap_logger.py
import logging
import os


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
