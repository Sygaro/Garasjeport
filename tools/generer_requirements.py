#!/usr/bin/env python3
# Fil: generer_requirements.py
# Formål: Oppdager faktisk brukte imports og lager minimal requirements.txt

import os
import re
import subprocess
from collections import defaultdict
from difflib import unified_diff
from datetime import datetime

PROSJEKTROT = os.getcwd()
EKSKLUDER_MAPPER = {'venv', '.venv', '__pycache__', '.git', '.idea', '.mypy_cache'}
IMPORT_MØNSTER = re.compile(r'^(?:from|import)\s+([a-zA-Z0-9_\.]+)')

# Enkel mapping fra import-navn til pip-pakkenavn der de avviker
PAKKE_MAPPING = {
    'PIL': 'Pillow',
    'flask': 'Flask',
    'flask_socketio': 'Flask-SocketIO',
    'RPi': 'RPi.GPIO',
    'gpiozero': 'gpiozero',
    'dotenv': 'python-dotenv',
    'lgpio': 'lgpio',
    'dropbox': 'dropbox',
}

def finn_imports():
    imports = set()
    for root, dirs, files in os.walk(PROSJEKTROT):
        dirs[:] = [d for d in dirs if d not in EKSKLUDER_MAPPER]
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, encoding='utf-8') as f:
                        for linje in f:
                            match = IMPORT_MØNSTER.match(linje.strip())
                            if match:
                                moduler = match.group(1).split('.')[0]
                                imports.add(moduler)
                except (UnicodeDecodeError, OSError) as e:
                    print(f"⚠️  Hopper over {file_path}: {e}")
    return imports


def hent_installerte_pakker():
    pip_liste = subprocess.check_output(['pip', 'freeze'], text=True).splitlines()
    pip_dict = {}
    for linje in pip_liste:
        if '==' in linje:
            navn, versjon = linje.strip().split('==')
            pip_dict[navn] = versjon
    return pip_dict

def bygg_requirements(imports, pip_dict):
    krav = {}
    for imp in imports:
        pipnavn = PAKKE_MAPPING.get(imp, imp)
        if pipnavn in pip_dict:
            krav[pipnavn] = pip_dict[pipnavn]
    return krav

def last_gammel_requirements():
    krav = {}
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', encoding='utf-8') as f:
            for linje in f:
                if '==' in linje:
                    navn, versjon = linje.strip().split('==')
                    krav[navn] = versjon
    return krav

def sammenlign_and_vis_diff(gammel, ny):
    gammel_linjer = [f"{k}=={v}" for k,v in sorted(gammel.items())]
    ny_linjer = [f"{k}=={v}" for k,v in sorted(ny.items())]
    diff = unified_diff(gammel_linjer, ny_linjer, fromfile='gammel', tofile='ny', lineterm='')
    for linje in diff:
        print(linje)

def main():
    print("🔎 Søker etter faktisk brukte imports...")
    imports = finn_imports()
    pip_dict = hent_installerte_pakker()
    krav = bygg_requirements(imports, pip_dict)

    gammel_krav = last_gammel_requirements()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if gammel_krav:
        backup_fil = f"requirements_backup_{timestamp}.txt"
        os.rename('requirements.txt', backup_fil)
        print(f"📦 Eksisterende requirements.txt er backupet som {backup_fil}")

    with open('requirements.txt', 'w', encoding='utf-8') as f:
        for navn, versjon in sorted(krav.items()):
            f.write(f"{navn}=={versjon}\n")

    print("\n🔧 Endringer fra gammel til ny requirements.txt:")
    sammenlign_and_vis_diff(gammel_krav, krav)

    print("\n✅ Ny requirements.txt generert basert på faktisk brukte imports.")

if __name__ == "__main__":
    main()
