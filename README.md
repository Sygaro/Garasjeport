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
```bash
git clone https://github.com/<ditt-brukernavn>/garasjeport_v1.04.git
cd garasjeport_v1.04
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🌐 Tilgang
- Web: `http://<din-raspberry-ip>:5000`
- API: `/api/config/gpio`, `/api/status/port1`, osv.

## 🤝 Lisens
Se [LICENSE](LICENSE)
