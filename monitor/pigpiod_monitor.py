import os
import time
import subprocess
from datetime import datetime
from utils.bootstrap_logger import log_to_bootstrap

from config import config_paths as paths
STATUS_FILE = paths.PIGPIO_STATUS_PATH

def is_pigpiod_running():
    try:
        output = subprocess.check_output(["pgrep", "pigpiod"])
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False

def write_status(running, restarts, last_restart):
    os.makedirs(paths.STATUS_DIR, exist_ok=True)
    with open(STATUS_FILE, "w") as f:
        f.write('{\n')
        f.write(f'  "pigpiod_running": {str(running).lower()},\n')
        f.write(f'  "last_checked": "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}",\n')
        f.write(f'  "restarts": {restarts},\n')
        f.write(f'  "last_restart_time": "{last_restart}"\n')
        f.write('}\n')

restarts = 0
failures = 0
max_backoff = 60

while True:
    running = is_pigpiod_running()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not running:
        log_to_bootstrap("pigpiod ikke kjørende – forsøker oppstart...")
        os.system("sudo pigpiod")
        time.sleep(2)

        if is_pigpiod_running():
            restarts += 1
            failures = 0
            log_to_bootstrap("pigpiod startet OK")
            write_status(True, restarts, now)
        else:
            failures += 1
            log_to_bootstrap("pigpiod feilet ved oppstart")
            write_status(False, restarts, "-")
            time.sleep(min(2 ** failures, max_backoff))
    else:
        write_status(True, restarts, now)
        time.sleep(10)
