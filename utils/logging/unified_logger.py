# Filnavn: utils/logging/unified_logger.py

import logging
import logging.handlers
import threading
import os
import json

from config import config_paths
from config import log_levels
from config import log_categories

# --- Colorama for console farger ---
try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init(autoreset=True)
    COLORAMA_ENABLED = True
except ImportError:
    COLORAMA_ENABLED = False

# --- Farget formatter for console ---
class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        "ERROR": Fore.RED,
        "WARNING": Fore.YELLOW,
        "CRITICAL": Fore.RED + Style.BRIGHT,
        "INFO": Fore.GREEN,
        "DEBUG": Fore.CYAN,
    }
    CAT_COLOR = Fore.MAGENTA
    RESET = Style.RESET_ALL

    def format(self, record):
        msg = super().format(record)
        # Fargelegg [LEVEL] uansett hvor i linjen den er
        for level, color in self.LEVEL_COLORS.items():
            tag = f"[{level}]"
            msg = msg.replace(tag, f"{color}{tag}{self.RESET}")
        # Fargelegg første kategori-tag (f.eks. [system]), men IKKE [BOOTSTRAP]
        # Bruk regex for å finne første [noe] etter [LEVEL]
        import re
        # Finn alle tags av formen [ord]
        tags = list(re.finditer(r"\[[a-zA-Z0-9_]+\]", msg))
        # Vi vil farge NESTE tag etter [LEVEL]
        for i, match in enumerate(tags):
            if any(match.group(0) == f"[{lvl}]" for lvl in self.LEVEL_COLORS):
                if i+1 < len(tags):
                    cat_tag = tags[i+1].group(0)
                    if cat_tag != "[BOOTSTRAP]":
                        msg = msg.replace(cat_tag, f"{self.CAT_COLOR}{cat_tag}{self.RESET}", 1)
                break
        return msg

# --- LoggerAdapter for kategori ---
class CategoryAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs["extra"] = kwargs.get("extra", {})
        kwargs["extra"]["category"] = self.extra.get("category", "unknown_category")
        # NB: IKKE sett "name" i extra! Det gir KeyError.
        return msg, kwargs

# --- Trådsikker logger-cache ---
_loggers = {}
_lock = threading.RLock()

def load_logging_config():
    """
    Leser logging config fra JSON.
    Fallback til default hvis fil mangler eller er korrupt.
    """
    path = getattr(config_paths, "CONFIG_LOGGING_PATH", None)
    if path and os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[LOGGER] FEIL ved lesing av config_logging.json: {e}")
    # Default fallback
    return {
        "max_file_size_mb": 10,
        "max_backups_files": 5,
        "timestamp_format": "%Y-%m-%d %H:%M:%S",
        "log_settings": {},
    }

def _get_valid_category(category):
    """
    Returnerer gyldig kategori hvis finnes i log_categories.py (dict-nøkler),
    ellers fallback til unknown_category.
    """
    try:
        categories_dict = getattr(log_categories, "LOG_CATEGORIES", {})
        cat_norm = category.lower().strip()
        valid = set(key.lower().strip() for key in categories_dict.keys())
        if cat_norm in valid:
            return cat_norm
    except Exception:
        pass
    return "unknown_category"

def _get_valid_level(level_str):
    """
    Returnerer integer-nivå for logging.
    Støtter custom nivå via log_levels.py, ellers standard logging.
    """
    try:
        if hasattr(log_levels, "LEVELS") and level_str.upper() in log_levels.LEVELS:
            return log_levels.LEVELS[level_str.upper()]
    except Exception:
        pass
    return getattr(logging, level_str.upper(), logging.INFO)

def get_logger(name, category="system", source=None):
    """
    Hoved-entrypoint for logging i hele systemet.
    Brukes slik:
        logger = get_logger("GarageController", category="port_activity", source="API")
        logger.info("Port åpnet")
    name: Modulnavn eller logisk navn (str)
    category: Kategori ("system", "api", "port_activity", etc.) (str)
    source: Tilleggsinfo for logger-navn (str, valgfritt)
    """
    global _loggers
    key = (name, category, source)
    with _lock:
        if key in _loggers:
            return _loggers[key]

        config = load_logging_config()
        valid_category = _get_valid_category(category)
        log_settings = config.get("log_settings", {})

        # Robust: Finn settings for kategori, fallback til unknown_category, så tom defaults
        settings = log_settings.get(valid_category)
        if not settings:
            valid_category = "unknown_category"
            settings = log_settings.get(valid_category)
        if not settings:
            # Siste fallback: harde defaults
            settings = {
                "file_enabled": True,
                "console_enabled": True,
                "file_level": "INFO",
                "console_level": "INFO",
                "format": "plain"
            }

        # Formatter-streng med kategori og navn
        timestamp_fmt = config.get("timestamp_format", "%Y-%m-%d %H:%M:%S")
        fmt_str = "%(asctime)s [%(levelname)s] [%(category)s] [%(name)s] %(message)s"
        formatter = logging.Formatter(fmt_str, datefmt=timestamp_fmt)
        color_formatter = ColorFormatter(fmt_str, datefmt=timestamp_fmt)

        logger = logging.getLogger(f"{name}_{valid_category}_{source or '-'}")
        logger.name = name
        logger.setLevel(_get_valid_level(settings.get("file_level", "INFO")))

        # Slett gamle handlers hvis loggeren rebrukes (kan skje i dev/test)
        if logger.hasHandlers():
            logger.handlers.clear()

        # Filhandler med rotasjon
        if settings.get("file_enabled", True):
            log_dir = getattr(config_paths, "LOG_DIR", ".")
            file_path = os.path.join(log_dir, f"{valid_category}.log")
            max_bytes = int(config.get("max_file_size_mb", 10)) * 1024 * 1024
            backup_count = int(config.get("max_backups_files", 5))
            try:
                os.makedirs(log_dir, exist_ok=True)
                fh = logging.handlers.RotatingFileHandler(
                    file_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
                )
                fh.setFormatter(formatter)
                fh.setLevel(_get_valid_level(settings.get("file_level", "INFO")))
                logger.addHandler(fh)
            except Exception as e:
                print(f"[LOGGER] FEIL ved oppsett av loggfil {file_path}: {e}")

        # Console handler – med farger
        if settings.get("console_enabled", True):
            ch = logging.StreamHandler()
            ch.setFormatter(color_formatter)
            ch.setLevel(_get_valid_level(settings.get("console_level", "INFO")))
            logger.addHandler(ch)

        logger.propagate = False

        # WRAP logger i CategoryAdapter slik at category alltid følger med til formatter!
        logger = CategoryAdapter(logger, {"category": valid_category})

        _loggers[key] = logger
        return logger
