# Fil: backup.py
# Håndtering av konfigurasjonsbackup og gjenoppretting

import os
import shutil
import datetime

BACKUP_DIR = "backups"

def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)

def create_backup(config_path="config.json"):
    ensure_backup_dir()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(BACKUP_DIR, f"config_backup_{timestamp}.json")
    shutil.copyfile(config_path, dest)
    return dest

def list_backups():
    ensure_backup_dir()
    return sorted(os.listdir(BACKUP_DIR), reverse=True)

def restore_backup(filename, config_path="config.json"):
    ensure_backup_dir()
    src = os.path.join(BACKUP_DIR, filename)
    if os.path.exists(src):
        shutil.copyfile(src, config_path)
        return True
    return False
