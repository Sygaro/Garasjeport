import subprocess
import datetime
import os

from utils.bootstrap_logger import log_to_bootstrap

def check_or_start_pigpiod():
    try:
        subprocess.run(["pgrep", "pigpiod"], check=True, stdout=subprocess.DEVNULL)
        print("[BOOTSTRAP] pigpiod kjører")
        log_to_bootstrap("pigpiod allerede kjørende")
    except subprocess.CalledProcessError:
        print("[BOOTSTRAP] pigpiod kjører ikke – prøver å starte...")
        log_to_bootstrap("pigpiod ikke funnet – forsøker å starte")

        try:
            subprocess.run(["sudo", "pigpiod"], check=True)
            print("[BOOTSTRAP] pigpiod startet")
            log_to_bootstrap("pigpiod startet OK")
        except Exception as e:
            err_msg = f"FEIL: Kunne ikke starte pigpiod: {e}"
            print(f"[BOOTSTRAP][ERROR] {err_msg}")
            log_to_bootstrap(err_msg)
