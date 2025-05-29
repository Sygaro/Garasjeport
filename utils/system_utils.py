import subprocess
import datetime
import os
from utils.logging.unified_logger import get_logger

logger = get_logger("system_utils", category="system")


def check_or_start_pigpiod():
    try:
        subprocess.run(["pgrep", "pigpiod"], check=True, stdout=subprocess.DEVNULL)
        #print("[BOOTSTRAP] pigpiod kjører")
        logger.info("pigpiod allerede kjørende")
    except subprocess.CalledProcessError:
        #print("[BOOTSTRAP] pigpiod kjører ikke – prøver å starte...")
        logger.warning("pigpiod ikke funnet – forsøker å starte")

        try:
            subprocess.run(["sudo", "pigpiod"], check=True)
            #print("[BOOTSTRAP] pigpiod startet")
            logger.info("pigpiod startet OK")
        except Exception as e:
            err_msg = f"FEIL: Kunne ikke starte pigpiod: {e}"
            #print(f"[BOOTSTRAP][ERROR] {err_msg}")
            logger.error(err_msg)
