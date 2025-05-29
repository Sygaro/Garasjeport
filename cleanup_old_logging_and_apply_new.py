
import os
import re

IGNORED_DIRS = {"venv", "__pycache__", ".git"}
PROJECT_ROOT = os.getcwd()

# Mønstre for gammel logging som skal fjernes eller oppdateres
OLD_LOG_IMPORTS = [
    r"from utils\.garage_logger import .*",
    r"from utils\.log_utils import .*",
    r"from utils\.logger_factory import .*",
]
OLD_LOG_FUNCTIONS = [
from logging_system.logger_manager import get_logger
    r"log_\w+\(.*?\)",  # funksjonskall som get_logger().info(), log_action() osv.
]
FILES_TO_REMOVE = ["utils/log_utils.py", "utils/logger_factory.py"]

# Ny import som skal legges til om nødvendig
NEW_LOG_IMPORT = "from logging_system.logger_manager import get_logger"

# Logger endringer her
log_file = open("log_migrasjon_endringer.txt", "w")

def should_ignore(path):
    return any(ignored in path.split(os.sep) for ignored in IGNORED_DIRS)

def update_file(filepath):
    updated = False
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        original = line
        for pattern in OLD_LOG_IMPORTS:
            line = re.sub(pattern, "", line)
        for pattern in OLD_LOG_FUNCTIONS:
            if re.search(pattern, line):
                line = "#" + line if not line.strip().startswith("#") else line
                updated = True
        if original != line:
            updated = True
        new_lines.append(line)

    # Legg til ny import hvis vi fjernet gammel og den ikke finnes
    if updated and NEW_LOG_IMPORT not in "".join(new_lines):
        new_lines.insert(0, NEW_LOG_IMPORT + "\n")
        updated = True

    if updated:
        with open(filepath, "w", encoding="utf-8", errors="ignore") as f:
            f.writelines(new_lines)
        log_file.write(f"Oppdatert: {filepath}\n")

def remove_old_files():
    for rel_path in FILES_TO_REMOVE:
        full_path = os.path.join(PROJECT_ROOT, rel_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            log_file.write(f"Slettet: {rel_path}\n")

def main():
    for root, _, files in os.walk(PROJECT_ROOT):
        if should_ignore(root):
            continue
        for file in files:
            if file.endswith(".py"):
                update_file(os.path.join(root, file))
    remove_old_files()
    print("Rydding fullført. Endringer loggført i 'log_migrasjon_endringer.txt'.")

if __name__ == "__main__":
    main()
