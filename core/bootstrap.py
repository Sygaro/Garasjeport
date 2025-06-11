# core/bootstrap.py

import os
import json
import shutil
import subprocess
import time
from datetime import datetime
from config import config_paths as paths
from utils.file_utils import ensure_dir_exists
from utils.bootstrap_logger import get_bootstrap_logger, shutdown_bootstrap_logger


def load_bootstrap_config():
    """
    Leser config for bootstrap/logging fra paths.CONFIG_BOOTSTRAP_LOGGING_PATH.
    Returnerer tomt dict hvis fil mangler/feiler.
    """
    config_path = getattr(paths, "CONFIG_BOOTSTRAP_PATH", None)
    if not config_path or not os.path.isfile(config_path):
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def validate_json_file(path, description, logger):
    if not os.path.exists(path):
        logger.error(f"{description} mangler: {path}")
        return False
    try:
        with open(path, "r") as f:
            json.load(f)
    except json.JSONDecodeError:
        logger.error(f"{description} er ikke gyldig JSON: {path}")
        return False
    return True

def ensure_directories(directories, logger):
    created = []
    for directory in directories:
        logger.debug(f"Sjekker katalog: {directory}")
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                logger.warning(f"Opprettet manglende mappe: {directory}")
                created.append(directory)
            except Exception as e:
                logger.error(f"Kunne ikke opprette mappe {directory}: {e}")
        else:
            logger.info(f"Verifisert mappe: {directory}")
    logger.debug(f"Kataloger opprettet: {created}")
    return created

def ensure_config_files(config_files, logger):
    missing, invalid, backed_up = [], [], []
    for file_path, description in config_files:
        logger.debug(f"Validerer config: {file_path} ({description})")
        if not validate_json_file(file_path, description, logger):
            if not os.path.exists(file_path):
                missing.append(file_path)
            else:
                invalid.append(file_path)
        else:
            # Backup hvis første gang (ingen kopi finnes)
            backup_path = os.path.join(paths.BACKUP_DIR, os.path.basename(file_path))
            if not os.path.exists(backup_path):
                try:
                    shutil.copy(file_path, backup_path)
                    logger.info(f"Tok sikkerhetskopi av {description} til {backup_path}")
                    backed_up.append(backup_path)
                except Exception as e:
                    logger.error(f"Kunne ikke ta backup av {file_path}: {e}")
    logger.debug(f"missing_files: {missing}")
    logger.debug(f"invalid_files: {invalid}")
    logger.debug(f"backed_up: {backed_up}")
    return missing, invalid, backed_up

def ensure_pigpiod_running(logger):
    logger.debug("Sjekker om pigpiod kjører ...")
    try:
        subprocess.check_output(["pgrep", "pigpiod"])
        logger.info("pigpiod er allerede kjørende")
        return True
    except subprocess.CalledProcessError:
        logger.warning("pigpiod er ikke startet – prøver å starte...")

    subprocess.run(["pigpiod"])
    time.sleep(1)

    try:
        subprocess.check_output(["pgrep", "pigpiod"])
        logger.info("pigpiod startet OK")
        return True
    except subprocess.CalledProcessError:
        logger.error("FEIL: pigpiod kunne ikke startes – systemet vil sannsynligvis feile")
        return False

def write_status(status: dict):
    """Lagrer status til fil for API eller frontend."""
    try:
        with open(paths.STATUS_BOOTSTRAP_PATH, "w") as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[BOOTSTRAP] Klarte ikke å skrive statusfil: {e}")

def check_python_version(min_version, logger):
    import sys
    if sys.version_info < min_version:
        logger.error(f"Feil Python-versjon! Krever >= {min_version}, fant {sys.version_info.major}.{sys.version_info.minor}")
        return False
    logger.debug(f"Python-versjon OK: {sys.version_info.major}.{sys.version_info.minor}")
    return True

def check_write_access(directories, logger):
    failed = []
    for dir_ in directories:
        try:
            testfile = os.path.join(dir_, ".writetest")
            with open(testfile, "w") as f:
                f.write("test")
            os.remove(testfile)
            logger.debug(f"Skrivetilgang OK for: {dir_}")
        except Exception as e:
            logger.error(f"Mangler skrivetilgang til {dir_}: {e}")
            failed.append(dir_)
    return failed

def check_disk_space(path, min_mb, logger):
    statvfs = os.statvfs(path)
    free_mb = statvfs.f_frsize * statvfs.f_bavail / (1024 * 1024)
    if free_mb < min_mb:
        logger.error(f"For lite diskplass i {path}: {free_mb:.1f} MB (minimum {min_mb} MB kreves)")
        return False
    logger.debug(f"Diskplass OK i {path}: {free_mb:.1f} MB ledig")
    return True

def check_single_instance(pid_file, logger):
    try:
        if os.path.isfile(pid_file):
            with open(pid_file, "r") as f:
                pid = int(f.read())
            # Prøv å sende signal 0 til prosessen (sjekker om den kjører)
            try:
                os.kill(pid, 0)
                logger.error(f"Instans kjører allerede med PID {pid}. Avslutter.")
                return False
            except OSError:
                logger.warning(f"Fant gammel pid-fil ({pid_file}), men prosessen kjører ikke. Sletter pid-fil.")
                os.remove(pid_file)
        # Skriv inn egen pid
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))
        logger.debug(f"Single instance kontroll: ok, pid={os.getpid()}")
        return True
    except Exception as e:
        logger.error(f"Feil i single instance-sjekk: {e}")
        return False

def validate_and_create_status_files(status_files, logger):
    """
    Sjekker at statusfiler finnes og er gyldig JSON.
    Oppretter fil med standardinnhold og logger warning hvis den mangler.
    """
    created = []
    warnings = []
    for file_path, description in status_files:
        if not os.path.isfile(file_path):
            # Opprett fil med default struktur
            try:
                # Eks: {"status": "no_data", "detail": "Opprettet av bootstrap – ingen data"}
                content = {
                    "status": "no_data",
                    "detail": f"Opprettet av bootstrap – ingen gyldig data for {description}"
                }
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(content, f, ensure_ascii=False, indent=2)
                logger.warning(f"Manglet statusfil og opprettet: {file_path}")
                created.append(file_path)
            except Exception as e:
                logger.error(f"Kunne ikke opprette statusfil {file_path}: {e}")
        else:
            # Sjekk at det er gyldig JSON
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    json.load(f)
                logger.debug(f"Gyldig statusfil: {file_path}")
            except Exception as e:
                logger.error(f"Ugyldig statusfil (må fikses): {file_path}: {e}")
                warnings.append(file_path)
    return created, warnings

def validate_logging_config(logger):
    """
    Sjekker at alle kategorier i log_categories.py også finnes i config_logging.json og motsatt.
    Sammenligningen gjøres case-insensitive og uten mellomrom.
    """
    from config import log_categories
    from config import config_paths
    import json, os

    # Normaliser til små bokstaver og ingen whitespace
    categories = set(cat.lower().strip() for cat in getattr(log_categories, "LOG_CATEGORIES", []))
    config_path = getattr(config_paths, "CONFIG_LOGGING_PATH", None)
    if not config_path or not os.path.isfile(config_path):
        logger.error(f"Fant ikke logging-config: {config_path}")
        return False

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    config_cats = set(cat.lower().strip() for cat in config.get("log_settings", {}).keys())

    missing = [cat for cat in categories if cat not in config_cats]
    missing_in_py = [cat for cat in config_cats if cat not in categories]

    if missing:
        logger.warning(f"Følgende loggkategorier mangler i config_logging.json: {missing}")
    if missing_in_py:
        logger.warning(f"Følgende kategorier i config_logging.json mangler i log_categories.py: {missing_in_py}")

    if not missing and not missing_in_py:
        logger.info("Alle loggkategorier er definert og synkronisert mellom log_categories.py og config_logging.json.")
    return not (missing or missing_in_py)




def run_bootstrap():
    logger = get_bootstrap_logger()
    logger.info("Starter bootstrap ...")

    # Last config for å sjekke om optional skal inkluderes
    bootstrap_config = load_bootstrap_config()
    check_optional = bootstrap_config.get("check_optional_directories", False)
    logger.debug(f"check_optional_directories: {check_optional}")

# --- Valider logging-config før systemet går videre ---
    logging_config_ok = validate_logging_config(logger)
    if not logging_config_ok:
        logger.warning("Det er mangler eller mismatch mellom log_categories.py og config_logging.json. Sjekk logg/warning.")


    # 1. Sjekk og opprett nødvendige (og ev. valgfrie) mapper
    required_dirs = list(paths.REQUIRED_DIRECTORIES)
    if check_optional and hasattr(paths, "OPTIONAL_DIRECTORIES"):
        required_dirs += list(paths.OPTIONAL_DIRECTORIES)
        logger.debug(f"Inkluderer OPTIONAL_DIRECTORIES: {paths.OPTIONAL_DIRECTORIES}")
    logger.debug(f"Directories to check: {required_dirs}")
    created_dirs = ensure_directories(required_dirs, logger)

    # 2. Sjekk nødvendige configfiler (hentes fra config_paths.py)
    config_files = getattr(paths, "REQUIRED_CONFIG_FILES", [])
    logger.debug(f"Config-filer som skal valideres: {config_files}")
    missing_files, invalid_files, backed_up = ensure_config_files(config_files, logger)

    # 3. Sjekk pigpiod
    pigpiod_ok = ensure_pigpiod_running(logger)
    logger.debug(f"pigpiod_ok: {pigpiod_ok}")

    # Python-versjon
    python_ok = check_python_version((3, 10), logger)

    # Sjekk skrivetilgang
    required_dirs = list(paths.REQUIRED_DIRECTORIES)
    write_failed = check_write_access(required_dirs, logger)

    # Diskplass (på log-dir eller valgt hovedkatalog)
    disk_ok = check_disk_space(paths.LOG_DIR, min_mb=50, logger=logger)

    # Single instance (f.eks. bruk en pid-fil i TEMP_DIR)
    #pid_file = os.path.join(paths.TEMP_DIR, "garasjeport.pid")
    pid_file = getattr(paths, "PID_FILE", None)

    single_ok = check_single_instance(pid_file, logger)

      # Sjekk statusfiler (definert i config_paths.py)
    status_files = getattr(paths, "REQUIRED_STATUS_FILES", [])
    created_status, warnings_status = validate_and_create_status_files(status_files, logger)

    # 4. Lag status
    status = {
        "timestamp": datetime.now().isoformat(),
        "created_dirs": created_dirs,
        "missing_files": missing_files,
        "invalid_files": invalid_files,
        "backed_up": backed_up,
        "pigpiod_ok": pigpiod_ok,
        "python_ok": python_ok,
        "write_failed": write_failed,
        "disk_ok": disk_ok,
        "single_instance_ok": single_ok,
       "created_status_files": created_status,
        "warnings_status_files": warnings_status,
        "ok": not missing_files and not invalid_files and pigpiod_ok,
        "logging_config_ok": logging_config_ok,
        "details": ""
    }
     # Sett samlet ok-status:
    status["ok"] = all([
        python_ok,
        disk_ok,
        single_ok,
        logging_config_ok,
        not write_failed,
        # ...legg til andre kritiske tester...
    ])
    logger.debug(f"status: {status}")

    if status["ok"]:
        logger.info("Bootstrap ferdig – alle sjekker OK.")
        print("[BOOTSTRAP] === OK: Klar til drift ===")
    else:
        logger.error("Bootstrap: Feil under oppstart! Sjekk detaljer.")
        print("[BOOTSTRAP] FEIL: Sjekk bootstrap.log")

    # 5. Skriv status til fil
    write_status(status)

    # 6. Avslutt logger
    shutdown_bootstrap_logger()

    return status

# For testing: kjør direkte
if __name__ == "__main__":
    run_bootstrap()
