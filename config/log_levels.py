# Fil: config/log_levels.py

import logging

# Egendefinerte nivåer
CUSTOM_LOG_LEVELS = {
    "CHANGE": 25,
    "TIMING": 15,

    "SECURITY": 35
}

# Legg til navn i logging-systemet
for name, level in CUSTOM_LOG_LEVELS.items():
    logging.addLevelName(level, name)

# Gjør dem tilgjengelig for andre moduler
LOG_LEVELS = {
    **{
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET,
    },
    **CUSTOM_LOG_LEVELS,
}
