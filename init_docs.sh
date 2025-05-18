#!/bin/bash

# Lager .md-filer for GitHub-prosjektet

echo "📄 Lager README.md"
cat <<EOF > README.md
# Garasjeportkontrollsystem

Et modulært, webbasert styringssystem for to garasjeporter, bygget for Raspberry Pi Zero 2 W og Raspberry Pi 5.

## 🚀 Funksjoner
- Kontroll av to porter via GPIO (rele + sensorer)
- Web-UI for status og manuell styring
- API-integrasjon for Homey eller andre smart-hubber
- Logging, backup, konfig-redigering og gjenoppretting
- Automatisk deteksjon av sensorfeil, stopp, og "delvis åpen"
- Polling-intervall og pinner er konfigurerbare
- Designet for å kjøre som systemtjeneste

## 🛠 Installasjon
\`\`\`bash
git clone https://github.com/<ditt-brukernavn>/garasjeport_v1.04.git
cd garasjeport_v1.04
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

## 🌐 Tilgang
- Web: \`http://<din-raspberry-ip>:5000\`
- API: \`/api/config/gpio\`, \`/api/status/port1\`, osv.

## 🤝 Lisens
Se [LICENSE](LICENSE)
EOF

echo "📄 Lager LICENSE (MIT)"
cat <<EOF > LICENSE
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software")...
[full MIT-tekst her hvis ønskelig]
EOF

echo "📄 Lager CHANGELOG.md"
cat <<EOF > CHANGELOG.md
# Endringslogg

## [1.04] – 2025-05-18
### Endret
- Fullstendig modulbasert struktur
- Ny konfigeditor med tabs og API-støtte
- Logging og rotasjon fra config

### Fjernet
- Gammel polling og kalibreringskode
EOF

echo "📄 Lager CONTRIBUTING.md"
cat <<EOF > CONTRIBUTING.md
# Bidrag

Takk for at du vurderer å bidra! Følg disse reglene:

- Fork prosjektet og lag en egen branch
- Én endring per pull request
- Beskriv hvorfor endringen er nyttig
- Følg Python PEP8 og navnekonvensjoner

## Lokalt oppsett
\`\`\`bash
git clone ...
cd prosjekt
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`
EOF

echo "📄 Lager CODE_OF_CONDUCT.md"
cat <<EOF > CODE_OF_CONDUCT.md
# Code of Conduct

Alle bidragsytere forventes å opptre med respekt. Vi godtar ikke:

- Trakassering, diskriminering
- Nedlatende språk
- Avbrytelser eller trolling

Kontakt [din e-post] ved alvorlige brudd.
EOF

echo "✅ Dokumentasjonen er klar!"
