import os
import re

PROJECT_ROOT = "."
LOG_FILE = "log_migrasjon_endringer.txt"
LOG_SYSTEM_IMPORT = "from logging_system.logger_manager import get_logger"

old_log_functions = {
    "log_status": "info",
    "log_error": "error",
    "log_action": "info",
    "log_timing": "info",
    "log_sensor_data": "info",
    "log_debug": "debug"
}

old_imports = [
    "from utils.garage_logger import",
    "from utils.logger_factory import",
    "from garage_logger import",
    "from logger_factory import"
]

removed_files = [
    "utils/garage_logger.py",
    "utils/logger_factory.py",
    "utils/log_utils.py"
]

def log_change(log_entries, filepath, lineno, old, new):
    log_entries.append(f"{filepath}:{lineno}: {old.strip()} => {new.strip()}")

def update_file(filepath, log_entries):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        log_entries.append(f"SKIPPET: {filepath} kunne ikke leses ({str(e)})")
        return

    updated = False
    new_lines = []
    inserted_import = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Fjern gamle imports
        if any(stripped.startswith(old) for old in old_imports):
            log_change(log_entries, filepath, i + 1, line, "# Fjernet gammel import")
            continue

        # Sett inn ny import hvis vi finner gammel logging
        if not inserted_import and any(func in stripped for func in old_log_functions.keys()):
            new_lines.append(LOG_SYSTEM_IMPORT + "\n")
            inserted_import = True

        # Erstatt gamle log-funksjoner med get_logger
        replaced = False
        for old_func, new_func in old_log_functions.items():
            pattern = rf"{old_func}\((.*?)\)"
            if re.search(pattern, stripped):
                new_line = re.sub(pattern, rf"get_logger(\1).{new_func}(\1)", line)
                log_change(log_entries, filepath, i + 1, line, new_line)
                new_lines.append(new_line)
                replaced = True
                updated = True
                break
        if not replaced:
            new_lines.append(line)

    if updated:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

def main():
    log_entries = []
    for root, _, files in os.walk(PROJECT_ROOT):
        if "venv" in root or "__pycache__" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                update_file(os.path.join(root, file), log_entries)

    # Slett gamle logger hvis de finnes
    for f in removed_files:
        if os.path.exists(f):
            os.remove(f)
            log_entries.append(f"FJERNET: {f}")

    with open(LOG_FILE, "w", encoding="utf-8") as log:
        for entry in log_entries:
            log.write(entry + "\n")

if __name__ == "__main__":
    main()
