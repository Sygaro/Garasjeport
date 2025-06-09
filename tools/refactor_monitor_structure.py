import os
import shutil
from pathlib import Path
import fileinput
import sys

PROJECT_ROOT = Path(__file__).resolve().parent

file_moves = {
    PROJECT_ROOT / "utils" / "sensor_monitor.py": PROJECT_ROOT / "monitor" / "port_sensor_monitor.py",
    PROJECT_ROOT / "monitor" / "sensor_monitor_task.py": PROJECT_ROOT / "monitor" / "env_sensor_monitor_task.py",
}

replacement_map = {
    "utils.sensor_monitor": "monitor.port_sensor_monitor",
    "monitor.sensor_monitor_task": "monitor.env_sensor_monitor_task"
}

dry_run = "--dry-run" in sys.argv

# Flytt og omdøp filer
for src, dst in file_moves.items():
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        print(f"Flytter: {src} → {dst}")
        if not dry_run:
            shutil.move(str(src), str(dst))
    else:
        print(f"ADVARSEL: Fant ikke {src}")

# Oppdater import-stier i alle .py-filer
for py_file in PROJECT_ROOT.rglob("*.py"):
    if py_file.name == Path(__file__).name:
        continue  # hopp over scriptet selv

    try:
        with open(py_file, encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"[SKIPPET] Kunne ikke lese {py_file} som UTF-8")
        continue

    original = content
    for old, new in replacement_map.items():
        content = content.replace(old, new)

    if content != original:
        print(f"[OPPDATERER] {py_file}")
        if not dry_run:
            with open(py_file, "w", encoding="utf-8") as f:
                f.write(content)

print("✅ Refaktorering fullført.")
