# Filnavn: utils/bootstrap_logger.py

"""
Dedikert logger for bootstrap/init-fasen.
Henter loggnivå, formatter, konsoll/filvalg fra config/config_bootstrap.json via CONFIG_BOOTSTRAP_PATH.
Skal kun brukes til bootstrap – unified_logger tar over etter oppstart.
"""

import logging
import os
import json
from config import config_paths


# --- Legg til colorama! ---
try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init(autoreset=True)
    COLORAMA_ENABLED = True
except ImportError:
    COLORAMA_ENABLED = False



_bootstrap_logger = None


class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        "ERROR": Fore.RED,
        "WARNING": Fore.YELLOW,
        "CRITICAL": Fore.RED + Style.BRIGHT,
        "INFO": Fore.GREEN,
        "DEBUG": Fore.CYAN,
    }
    BOOTSTRAP_COLOR = Fore.YELLOW  # Velg ønsket farge for [BOOTSTRAP]
    RESET = Style.RESET_ALL

    def format(self, record):
        base = super().format(record)
        # Fargelegg [BOOTSTRAP]
        if "[BOOTSTRAP]" in base:
            base = base.replace("[BOOTSTRAP]", f"{self.BOOTSTRAP_COLOR}[BOOTSTRAP]{self.RESET}")

        # Fargelegg kun nivå-taggen (f.eks. [DEBUG])
        for level, color in self.LEVEL_COLORS.items():
            tag = f"[{level}]"
            if tag in base:
                base = base.replace(tag, f"{color}{tag}{self.RESET}")
                break  # Kun ett nivå per linje
        return base


def load_bootstrap_log_config():
    """
    Leser logginnstillinger fra config/config_bootstrap.json ('CONFIG_BOOTSTRAP_PATH').
    Returnerer default verdier hvis fil mangler/feiler.
    """
    # Default fallback hvis config mangler
    defaults = {
        "timestamp_format": "%Y-%m-%d %H:%M:%S",
        "bootstrap_log_settings": {
            "file_enabled": True,
            "file_level": "INFO",
            "console_enabled": True,
            "console_level": "INFO",
            "format": "plain"
        }
    }
    config_path = getattr(config_paths, "CONFIG_BOOTSTRAP_PATH", None)
    if not config_path or not os.path.isfile(config_path):
        print(f"[BOOTSTRAP] Fant ikke {config_path}, bruker default logging config.")
        return defaults
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            conf = json.load(f)
            # Sørg for at nødvendige nøkler finnes, ellers bruk defaults
            if "bootstrap_log_settings" not in conf:
                conf["bootstrap_log_settings"] = defaults["bootstrap_log_settings"]
            if "timestamp_format" not in conf:
                conf["timestamp_format"] = defaults["timestamp_format"]
            return conf
    except Exception as e:
        print(f"[BOOTSTRAP] Klarte ikke å lese {config_path}: {e}")
        return defaults

def get_log_level(level_str):
    """Returnerer logging-nivå fra tekst, eller INFO hvis ugyldig."""
    return getattr(logging, str(level_str).upper(), logging.INFO)


def get_bootstrap_logger():
    global _bootstrap_logger
    if _bootstrap_logger is not None:
        return _bootstrap_logger

    config = load_bootstrap_log_config()
    log_settings = config.get("bootstrap_log_settings", {})
    timestamp_format = config.get("timestamp_format", "%Y-%m-%d %H:%M:%S")
    formatter = logging.Formatter(
        "%(asctime)s [BOOTSTRAP] [%(levelname)s] %(message)s", datefmt=timestamp_format
    )
    color_formatter = ColorFormatter(
        "%(asctime)s [BOOTSTRAP] [%(levelname)s] %(message)s", datefmt=timestamp_format
    )

    logger = logging.getLogger("bootstrap")
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler (vanlig formatter)
    if log_settings.get("file_enabled", True):
        try:
            os.makedirs(os.path.dirname(config_paths.LOG_BOOTSTRAP_PATH), exist_ok=True)
            fh = logging.FileHandler(config_paths.LOG_BOOTSTRAP_PATH, encoding='utf-8')
            fh.setLevel(get_log_level(log_settings.get("file_level", "INFO")))
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception as e:
            print(f"[BOOTSTRAP] Klarte ikke å opprette/åpne loggfil: {e}")

    # Console handler (med farger)
    if log_settings.get("console_enabled", True):
        ch = logging.StreamHandler()
        ch.setLevel(get_log_level(log_settings.get("console_level", "INFO")))
        ch.setFormatter(color_formatter)  # KUN denne!
        logger.addHandler(ch)

    _bootstrap_logger = logger
    return logger


def shutdown_bootstrap_logger():
    """
    Fjerner alle handlers og nullstiller bootstrap-logger.
    Skal alltid kalles etter fullført bootstrap/init.
    """
    global _bootstrap_logger
    if _bootstrap_logger is not None:
        handlers = _bootstrap_logger.handlers[:]
        for handler in handlers:
            try:
                handler.close()
            except Exception:
                pass
            _bootstrap_logger.removeHandler(handler)
        _bootstrap_logger = None
