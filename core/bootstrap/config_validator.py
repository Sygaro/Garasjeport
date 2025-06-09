import os

REQUIRED_PATHS = [
    "config/config_logging.json",
    "config/log_levels.py",
    "config/log_categories.py"
]

def validate_config_paths(logger):
    all_valid = True
    for path in REQUIRED_PATHS:
        if not os.path.exists(path):
            logger.critical(f"Mangler påkrevd fil: {path}")
            all_valid = False
    return all_valid