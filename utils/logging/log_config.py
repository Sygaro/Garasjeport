# utils/logging/log_config.py
import json
import os
from config import config_paths

class LogConfig:
    def __init__(self):
        self.config_file = config_paths.LOGGING_CONFIG
        self.settings = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Logg-konfigurasjon ikke funnet: {self.config_file}")
        with open(self.config_file, "r") as f:
            return json.load(f)

    def get_category_config(self, category):
        return self.settings.get("log_settings", {}).get(category, {})

    def is_enabled(self, category):
        return self.get_category_config(category).get("enabled", False)

    def get_level(self, category):
        return self.get_category_config(category).get("level", "INFO").upper()

    def get_format(self, category):
        return self.get_category_config(category).get("format", "plain")

    def get_targets(self, category):
        return self.get_category_config(category).get("output", ["file"])
