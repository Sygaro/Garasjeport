import logging

LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "CHANGE": 23,
    "NOTICE": 25,
    "ACTIVITY": 29,  # Custom level for activity messages
    "TIMING": 35,  # Custom level for timing messages
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
