# Filnavn: utils/logging/unified_logger.py

import logging
import logging.handlers
import threading
import os
import json

from config import config_paths # Importer config_paths for logg-mappe og andre konfigurasjoner
from config import log_levels # Importer log_levels for tilpassede nivåer
from config import log_categories # Importer log_categories for gyldige kategorier

try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init(autoreset=True)
    COLORAMA_ENABLED = True
except ImportError:
    COLORAMA_ENABLED = False



# Forward declaration for monkeypatch:
class CategoryAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs["extra"] = kwargs.get("extra", {})
        kwargs["extra"]["category"] = self.extra.get("category", "unknown_category")
        kwargs["extra"]["source"] = self.extra.get("source", "-")
        return msg, kwargs

def _register_custom_levels_and_methods():
    def make_log_for_level(num):
        def log_for_level(self, message, *args, **kwargs):
            if self.isEnabledFor(num):
                self.log(num, message, *args, **kwargs)
        return log_for_level

    for name, num in log_levels.LEVELS.items():
        if not hasattr(logging, name):
            logging.addLevelName(num, name)
            setattr(logging.Logger, name.lower(), make_log_for_level(num))
        setattr(CategoryAdapter, name.lower(), make_log_for_level(num))

_register_custom_levels_and_methods()

# --- Farget formatter for console ---
class ColorFormatter(logging.Formatter):
    COLORAMA_COLORS = {
        "BLACK": Fore.BLACK, "RED": Fore.RED, "GREEN": Fore.GREEN,
        "YELLOW": Fore.YELLOW, "BLUE": Fore.BLUE, "MAGENTA": Fore.MAGENTA,
        "CYAN": Fore.CYAN, "WHITE": Fore.WHITE,
        "BRIGHT_RED": Fore.RED + Style.BRIGHT,
        "BRIGHT_YELLOW": Fore.YELLOW + Style.BRIGHT,
        "BRIGHT_GREEN": Fore.GREEN + Style.BRIGHT,
        "BRIGHT_CYAN": Fore.CYAN + Style.BRIGHT,
        "BRIGHT_MAGENTA": Fore.MAGENTA + Style.BRIGHT,
        "BRIGHT_BLUE": Fore.BLUE + Style.BRIGHT,
        "BRIGHT_WHITE": Fore.WHITE + Style.BRIGHT,
    }
    RESET = Style.RESET_ALL

    def __init__(self, fmt, datefmt, color_config=None):
        super().__init__(fmt, datefmt=datefmt)
        self.color_config = color_config or {}

    def format(self, record):
        msg = super().format(record)
        # LEVEL
        level = record.levelname
        color_map = self.color_config.get("level", {})
        color = self.COLORAMA_COLORS.get(color_map.get(level, ""), "")
        if color:
            msg = msg.replace(f"[{level}]", f"{color}[{level}]{self.RESET}")
        # CATEGORY
        cat = getattr(record, "category", None)
        cat_map = self.color_config.get("category", {})
        if cat:
            color = self.COLORAMA_COLORS.get(cat_map.get(cat, ""), "")
            if color:
                msg = msg.replace(f"[{cat}]", f"{color}[{cat}]{self.RESET}", 1)
        # NAME
        name = getattr(record, "name", None)
        name_map = self.color_config.get("name", {})
        if name:
            color = self.COLORAMA_COLORS.get(name_map.get(name, ""), "")
            if color:
                msg = msg.replace(f"[{name}]", f"{color}[{name}]{self.RESET}", 1)
        # SOURCE
        src = getattr(record, "source", None)
        src_map = self.color_config.get("source", {})
        if src:
            color = self.COLORAMA_COLORS.get(src_map.get(src, ""), "")
            if color:
                msg = msg.replace(f"[{src}]", f"{color}[{src}]{self.RESET}", 1)
        return msg

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
        "color_settings": {},
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
        fmt_str = "%(asctime)s [%(levelname)s] [%(category)s] [%(name)s] [%(source)s] %(message)s"
        color_settings = config.get("color_settings", {})
        formatter = logging.Formatter(fmt_str, datefmt=timestamp_fmt)
        color_formatter = ColorFormatter(fmt_str, datefmt=timestamp_fmt, color_config=color_settings)


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

        # WRAP logger i CategoryAdapter slik at category og source alltid følger med!
        logger = CategoryAdapter(logger, {"category": valid_category, "source": source or "-"})

        _loggers[key] = logger
        return logger
