# migrate_system_to_port_status.py
"""
Erstatter bruk av CONFIG_SYSTEM_PATH med CONFIG_PORT_STATUS_PATH i oppgitte filer.
Logger fil, linje, endring. Hopper over rene kommentarfelt eller dokstring-linjer.
"""

import os

files_to_update = [
    "./utils/config_loader.py",
    "./routes/api/timing_routes.py",
    "./core/system.py",
    "./core/system_init.py",
    "./core/garage_controller.py",
    "./config/config_paths.py"
]

logfile = "migrate_config_path.log"
log_entries = []

def migrate_file(filepath):
    changed = False
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for idx, line in enumerate(lines):
        original = line.rstrip("\n")
        # Bytt kun der linjen faktisk inneholder CONFIG_SYSTEM_PATH, men ikke i kommentar/dokstring alene
        if "CONFIG_SYSTEM_PATH" in original:
            # Sjekk om linjen er ren kommentar eller dokstring
            if original.strip().startswith("#") or original.strip().startswith('"') or original.strip().startswith("'"):
                # Ikke bytt i rene kommentarer, men logg at det finnes
                log_entries.append(f"{filepath}: line {idx+1}: kommentar/dokstring med CONFIG_SYSTEM_PATH (ingen endring): '{original}'")
                new_lines.append(line)
            else:
                new_line = line.replace("CONFIG_SYSTEM_PATH", "CONFIG_PORT_STATUS_PATH")
                log_entries.append(f"{filepath}: line {idx+1}: '{original}' --> '{new_line.rstrip()}'")
                new_lines.append(new_line)
                changed = True
        else:
            new_lines.append(line)

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    return changed

if __name__ == "__main__":
    print("Starter migrering av CONFIG_SYSTEM_PATH til CONFIG_PORT_STATUS_PATH...\n")
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
