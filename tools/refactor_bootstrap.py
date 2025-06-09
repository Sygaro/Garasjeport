import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = BASE_DIR / "core"
BOOTSTRAP_DIR = CORE_DIR / "bootstrap"
CONFIG_DIR = BASE_DIR / "config"
TOOLS_DIR = BASE_DIR / "tools"
LOG_CONFIG_FILE = CONFIG_DIR / "bootstrap_logging.json"

FILES_TO_CREATE = {
    BOOTSTRAP_DIR / "logger_initializer.py": '''
import json
import logging
from pathlib import Path

def setup_logger():
    config_path = Path("config/bootstrap_logging.json")
    if not config_path.exists():
        raise FileNotFoundError("Fant ikke bootstrap_logging.json")

    with config_path.open() as f:
        config = json.load(f)

    logger = logging.getLogger("bootstrap")
    logger.setLevel(getattr(logging, config.get("level", "INFO").upper(), logging.INFO))

    formatter_type = config.get("format", "plain")
    if formatter_type == "json":
        formatter = logging.Formatter('{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
    else:
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    if config.get("console", True):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if config.get("file", True):
        file_handler = logging.FileHandler(config.get("log_path", "logs/bootstrap.log"))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
''',

    BOOTSTRAP_DIR / "config_validator.py": '''
import os

REQUIRED_PATHS = [
    "config/config_logging.json",
    "config/log_levels.py",
    "config/log_categories.py"
]

def validate_config_paths(logger):
    all_valid = True
    for path in REQUIRED_PATHS:
        if not os.path.exists(path):
            logger.critical(f"Mangler påkrevd fil: {path}")
            all_valid = False
    return all_valid
''',

    CORE_DIR / "system_entrypoint.py": '''
def start():
    print("Starter hovedsystem (API, sensorer, monitor etc.)")
    # TODO: Implementer faktisk systemstart her
''',

    CONFIG_DIR / "bootstrap_logging.json": '''{
  "console": true,
  "file": true,
  "level": "INFO",
  "format": "plain",
  "log_path": "logs/bootstrap.log"
}'''
}

def safe_write(file_path, content):
    if file_path.exists():
        print(f"[!] Fil finnes allerede: {file_path}")
    else:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content.strip())
        print(f"[+] Opprettet: {file_path}")

def main():
    print("🚀 Starter refaktorering...")

    # 1. Flytt bootstrap.py → startup_manager.py
    original = CORE_DIR / "bootstrap.py"
    target = BOOTSTRAP_DIR / "startup_manager.py"
    if original.exists():
        BOOTSTRAP_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(original), str(target))
        print(f"[✓] Flyttet: {original} → {target}")
    else:
        print(f"[ ] Fant ikke bootstrap.py – hopper over flytting.")

    # 2. Omdøp app.py → main.py
    app_file = BASE_DIR / "app.py"
    main_file = BASE_DIR / "main.py"
    if app_file.exists():
        shutil.move(str(app_file), str(main_file))
        print(f"[✓] Omdøpt: app.py → main.py")
    else:
        print(f"[ ] Fant ikke app.py – hopper over omdøping.")

    # 3. Lag bootstrap-moduler
    for file_path, content in FILES_TO_CREATE.items():
        safe_write(file_path, content)

    print("✅ Refaktorering fullført.")

if __name__ == "__main__":
    main()
