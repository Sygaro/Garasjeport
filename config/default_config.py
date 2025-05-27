# config/default_config.py

DEFAULT_CONFIGS = {
    "config_gpio.json": {
        "relay_pins": {
            "port1": 14,
            "port2": 25
        },
        "sensor_pins": {
            "port1": {"open": 23, "closed": 24},
            "port2": {"open": 20, "closed": 21}
        }
    },
    "config_system.json": {
        "calibration": {},
        "polling_interval_ms": 2000
    },
    "config_logging.json": {
        "log_rotation_days": 30,
        "log_archive_retention_days": 90
    }
}

REQUIRED_LOG_FILES = [
    "activity.log",
    "status.log",
    "errors.log",
    "timing.log",
    "bootstrap.log",
    "sensor_data.log"
]
