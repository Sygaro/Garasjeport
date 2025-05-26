# Garasjeportkontrollsystem
Et robust og modulært system for styring og overvåkning av garasjeporter via Raspberry Pi, med støtte for pigpio, sensoravlesning, API, og systemovervåkning.

## Kom i gang

### Forutsetninger
- Raspberry Pi OS
- Python 3.11+
- pigpiod installert og aktivert (`sudo apt install pigpio && sudo systemctl enable pigpiod`)

### Kloning og oppstart
```bash
git clone https://github.com/<din-repo>/garasjeport_v1.06.git
cd garasjeport_v1.06
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

#### 🛠️ Strukturoversikt
md
## Prosjektstruktur

app.py – starter Flask-applikasjonen
core/ – init, controller og systembootstrap
utils/ – hjelpelogikk: logging, pigpio, config-loader etc
routes/ – REST-API-ruter (delt i moduler)
monitor/ – bakgrunnsjobber og overvåkning
config/ – konfigurasjonsfiler (.json)
logs/ – runtime logger

#### 🔌 API-dokumentasjon
```md
## API-eksempler

- `GET /api/status` – status for alle porter
- `POST /api/port/port1/open` – åpne port 1
- `GET /api/system/rpi_status` – systemstatus
- `GET /api/system/rpi_diagnostic` – diagnostikk og terskelvurdering
