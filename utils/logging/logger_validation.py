# Fil: utils/logging/logger_validation.py

import json
import os
import ast
from config import log_categories, config_paths

# Kategorier som er gyldige i config_logging.json, men ikke skal være i LOG_CATEGORIES
EXEMPT_CATEGORIES = {"console_debug"}

def validate_logging_config():
    """
    Validerer at alle kategorier i log_categories finnes i config_logging.json
    Rapporterer også moduler og linjer der ugyldige kategorier brukes,
    både via posisjonelle og navngitte argumenter.
    """
    path = config_paths.CONFIG_LOGGING_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Fant ikke loggkonfigurasjonsfil: {path}")

    with open(path, "r") as f:
        config = json.load(f)

    defined = set(config.get("log_settings", {}).keys())
    required = set(log_categories.LOG_CATEGORIES.keys())

    missing = required - defined
    extra = defined - required - EXEMPT_CATEGORIES

    if missing:
        print("\n⚠️  Manglende loggkategorier i config_logging.json:")
        for m in sorted(missing):
            print(f"  - {m}")

    if extra:
        print("\nℹ️  Ekstra kategorier i config_logging.json (ikke brukt i log_categories.py):")
        for e in sorted(extra):
            print(f"  - {e}")

    print("\n🔎 Søker etter bruk av ugyldige kategorier i kildekoden...")
    base_dir = os.path.dirname(os.path.dirname(__file__))
    problems_found = False

    for root, _, files in os.walk(base_dir):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as src:
                    content = src.read()
                    if "\x00" in content:
                        #print(f"  ⚠️  Hopper over fil med null-bytes: {fpath}")
                        continue
                    tree = ast.parse(content, filename=fname)
            except (SyntaxError, UnicodeDecodeError, ValueError):
                print(f"  ⚠️  Hopper over ikke-lesbar fil: {fpath}")
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and hasattr(node.func, "id") and node.func.id == "get_logger":
                    # Sjekk både posisjonelle og navngitte argumenter
                    # Posisjonell: get_logger("name", "category")
                    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                        cat = node.args[1].value
                        if cat not in required and cat not in EXEMPT_CATEGORIES:
                            problems_found = True
                            print(f"  🚨 {fpath}:{node.lineno} – Ugyldig kategori '{cat}' brukt i get_logger() [posisjonell]")

                    # Navngitt: get_logger(name, category="...")
                    keywords = {kw.arg: kw.value.s for kw in node.keywords if isinstance(kw.value, ast.Constant)}
                    if "category" in keywords and keywords["category"] not in required and keywords["category"] not in EXEMPT_CATEGORIES:
                        problems_found = True
                        print(f"  🚨 {fpath}:{node.lineno} – Ugyldig kategori '{keywords['category']}' brukt i get_logger() [navngitt]")

    if not problems_found:
        print("\n✅ Ingen bruk av ugyldige kategorier funnet i prosjektet.")


if __name__ == "__main__":
    validate_logging_config()
