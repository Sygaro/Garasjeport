# Systemarkitektur – Garasjeportprosjekt v1.06

Dette dokumentet forklarer den tekniske strukturen, modulene og hovedansvar for hver del av systemet. Målet er å gi en oversikt som gjør det enkelt å forstå, vedlikeholde og utvide løsningen.

---

## 🧠 Overordnet prinsipp

Systemet er bygd opp rundt en **modulær og skalerbar arkitektur**, hvor konfigurasjoner, GPIO-kontroll, API og overvåkning er separert i distinkte moduler med klart ansvar. All hardware-kontroll er gjort via `pigpio` og `pigpiod`.

---

## 📂 Katalogstruktur

```
├── app.py # Startpunkt for Flask-applikasjonen
├── core/ # Kontrollere og bootstrap-oppstart
│ ├── garage_controller.py # Hovedlogikk for portstyring
│ ├── bootstrap.py # Init, validering, sanitetssjekker
│ └── system.py # Initialiserer controller-instans
│
├── utils/ # Verktøy og tjenester
│ ├── relay_control.py # Styring av rele via pigpio
│ ├── sensor_monitor.py # Overvåkning av magnetsensorer
│ ├── pigpio_manager.py # Singleton-instans for pigpio.pi()
│ ├── garage_logger.py # Strukturert og fleksibel logging
│ ├── config_loader.py # Laster og validerer .json-konfig
│ ├── system_monitor.py # Overvåkning av RPi-ressurser
│ └── auth.py # API-tokenbeskyttelse
│
├── routes/
│ ├── api/ # Ruter for REST API
│ │ ├── port_routes.py
│ │ ├── status_routes.py
│ │ ├── timing_routes.py
│ │ ├── system_routes.py
│ │ └── init.py # Felles blueprint
│ └── web.py # Evt. fremtidig web-grensesnitt
│
├── monitor/ # Bakgrunnsoppgaver (async, systemd)
│ ├── pigpiod_monitor.py
│ ├── system_monitor_task.py
│
├── config/ # Konfigurasjonsfiler
│ ├── config_gpio.json
│ ├── config_system.json
│ ├── config_logging.json
│ ├── config_health.json
│ └── config_timing.json
│
├── logs/ # Loggfiler (genereres ved kjøring)
├── static/ # (valgfritt) Statisk frontend
└── templates/ # HTML (hvis frontend legges til)

```
---

## 🔌 Hovedkomponenter

### 1. `GarageController`
Sentral klasse for systemlogikk:

- Initierer `RelayControl` og `SensorMonitor`
- Håndterer åpne/lukke/stopp via puls
- Logger tidsdata (t0, t1, t2)
- Vedlikeholder portstatus og feilmarginer

### 2. `RelayControl`
Abstraherer pigpio-styring:

- Leser `relay_config` fra `config_gpio.json`
- Styrer puls til releutganger
- Tilbakestiller GPIO ved shutdown

### 3. `SensorMonitor`
Sensor-callbacks med pigpio:

- Leser og overvåker magnetsensorer
- Trigges på EITHER_EDGE
- Bruker `set_callback()` for tilknytning til `GarageController`

### 4. `Bootstrap`
Kjører tidlig i `app.py`:

- Validerer .json-konfig
- Logger til `bootstrap_status.json`
- Starter pigpiod hvis ikke aktiv
- Klargjør systemet før Flask starter

### 5. `pigpio_manager.py`
Sentral singleton-instans for pigpio:

- Unngår duplikate instanser
- `get_pi()` sikrer én global delt `pi`-instans
- Brukes av både rele og sensor-modul

---

## 🔐 API og routing

- **Modulbasert routing** i `routes/api/`
- Felles blueprint `api = Blueprint(..., url_prefix="/api")`
- Alle API-ruter er token-beskyttet (`@token_required`)
- Eksempler:
  - `GET /api/status`
  - `POST /api/port/port1/open`
  - `GET /api/system/rpi_status`
  - `GET /api/system/rpi_diagnostic`

---

## ⚙️ Konfigurasjonsfiler (.json)

| Filnavn               | Beskrivelse                                    |
|-----------------------|------------------------------------------------|
| `config_gpio.json`    | Definerer GPIO for rele og sensorer            |
| `config_system.json`  | Tidsdata og portstatus                         |
| `config_logging.json` | Logger-filer, rotasjon og nivåer               |
| `config_health.json`  | Varslingsgrenser for CPU, disk, minne          |
| `config_timing.json`  | Standardverdier (t0, t2, marginer etc)         |

---

## 📈 Logging

Logger er sentralisert i `GarageLogger`, og har støtte for:

- status.log
- error.log
- activity.log
- timing.log
- bootstrap.log

Loggformat følger en strukturert konvensjon med:
```text
[tidspunkt] [nivå] [kontekst]: melding
```

## 📊 Overvåkning
Pigpiod-monitor: Verifiserer at pigpiod kjører

System-monitor: Henter temperatur, disk/memory-bruk, oppdateringer

API: `/api/system/rpi_status`, `/api/system/rpi_diagnostic`


## 🔚 Avslutning og opprydding
Ved SIGINT:

controller.shutdown() kalles via atexit

Logger shutdown

Tilbakestiller GPIO og avslutter pigpio


## 📌 Fremtidige forbedringer
Frontend med status/visuell kontroll

WebSocket-basert sanntidsoppdatering

Systemd-tjenestefil

Automatisk fallback til manuell modus ved pigpiod-feil