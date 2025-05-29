
import os

# Konstanter som skal byttes
RENAMING_MAP = {
    "CONFIG_LOGGING_PATH": "CONFIG_LOGGING_PATH",
    "CONFIG_GPIO_PATH": "CONFIG_GPIO_PATH",
    "CONFIG_SYSTEM_PATH": "CONFIG_SYSTEM_PATH",
    "LOG_SENSOR_ENV_PATH": "LOG_SENSOR_ENV_PATH",
    "LOG_BOOTSTRAP_PATH": "LOG_BOOTSTRAP_PATH",
    "STATUS_PIGPIO_PATH": "STATUS_PIGPIO_PATH",
    "STATUS_BOOTSTRAP_PATH": "STATUS_BOOTSTRAP_PATH"
}

def replace_constants_in_file(filepath, renaming_map):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    modified = False
    new_lines = []
    changes = []

    for i, line in enumerate(lines):
        original_line = line
        for old, new in renaming_map.items():
            if old in line:
                line = line.replace(old, new)
        if line != original_line:
            modified = True
            changes.append((filepath, i + 1, original_line.strip(), line.strip()))
        new_lines.append(line)

    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    return changes

def main(project_dir):
    log = []
    for root, dirs, files in os.walk(project_dir):
        if any(ignored in root for ignored in ["venv", "__pycache__", ".git"]):
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                changes = replace_constants_in_file(filepath, RENAMING_MAP)
                log.extend(changes)

    print("\nEndringer utført:")
    for file, line, before, after in log:
        print(f"{file} [linje {line}]:\n  Før:  {before}\n  Etter: {after}\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Bruk: python refactor_config_paths.py <prosjektmappe>")
    else:
        main(sys.argv[1])
