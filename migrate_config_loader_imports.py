# migrate_imports.py
"""
Migrerer gamle imports fra utils.file_utils til oppdaterte helpers.
Logger alle endringer: filnavn, linjenummer, hva som er endret fra og til.
"""

import os

# Filer som skal migreres
files_to_update = [
    "./system/gpio_initializer.py",
    "./utils/relay_initializer.py",
    "./utils/status_helpers.py",
    "./utils/file_utils.py",
    "./utils/config_helpers.py",
    "./monitor/port_sensor_monitor.py",
    "./core/bootstrap.py",
    # tidl. migrerte:
    "./routes/api/system_routes.py",
    "./routes/api/timing_routes.py",
    "./monitor/system_monitor.py",
    "./monitor/environment_manager.py",
    "./monitor/system_monitor_task.py",
    "./core/system.py"
]

logfile = "migrate_file_utils.log"
log_entries = []

# Mapping av gamle -> nye imports
import_map = [
    # Kun imports av helpers, ikke filnavn-kommentarer
    ("from utils.file_utils import load_json", "from utils.file_utils import read_json"),
    ("from utils.file_utils import ensure_directory_exists", "from utils.file_utils import ensure_dir_exists"),
    # Eksisterende helpers beholdes, men evt. imports av read_json, write_json beholdes (men sjekk om de finnes i ny fil!)
]

# Enkel funksjon for å bytte ut flere imports på én gang
def replace_imports(line, filename, lineno):
    changed = False
    for old, new in import_map:
        if old in line:
            log_entries.append(f"{filename}: line {lineno}: '{line.rstrip()}' --> '{new}'")
            return new + "\n", True
    return line, changed

def migrate_file(filepath):
    changed = False
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        # Ignorer filnavn-kommentarer og linjer som kun dokumenterer filnavn
        if stripped.startswith("# file_utils.py") or "utils/file_utils.py" in stripped:
            new_lines.append(line)
            continue

        # Migrer imports iht. mappingen
        new_line, import_changed = replace_imports(line, filepath, idx+1)
        if import_changed:
            changed = True
            new_lines.append(new_line)
            continue

        # Fjern evt. kommenterte gamle imports
        if "# from utils.file_utils import" in stripped:
            log_entries.append(
                f"{filepath}: line {idx+1}: '{line.rstrip()}' --> (removed/commented out)"
            )
            changed = True
            continue

        # Retain all other lines
        new_lines.append(line)

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    return changed

if __name__ == "__main__":
    print("Starter migrering av file_utils-imports og load_config-imports...\n")
    files_changed = 0
    for relpath in files_to_update:
        if not os.path.exists(relpath):
            print(f"Finner ikke fil: {relpath}")
            continue
        changed = migrate_file(relpath)
        if changed:
            files_changed += 1
            print(f"Endret: {relpath}")
    print(f"\nTotalt endret {files_changed} filer.\n")
    with open(logfile, "w", encoding="utf-8") as f:
        for entry in log_entries:
            f.write(entry + "\n")
    print(f"Detaljert logg er lagret i {logfile}")
    print("Migrering fullført.")