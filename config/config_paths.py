# config/config_paths.py

"""
Definerer globale stier til viktige mapper i prosjektet.
Bruk disse i stedet for å hardkode "logs/", "config/" osv. i resten av koden.
"""

import os

# Roterer utgangspunktet til prosjektets rotmappe
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Absolutte stier til kjernemapper
LOG_DIR = os.path.join(BASE_DIR, "logs")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")  # valgfritt
DOCS_DIR = os.path.join(BASE_DIR, "docs")      # valgfritt
