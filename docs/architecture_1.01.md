# Arkitektur – Garasjeportprosjektet

Dette dokumentet gir en oversikt over systemarkitekturen i garasjeportprosjektet, med vekt på modularitet, fleksibilitet og robusthet. Det forklarer hvordan komponentene samhandler og hvordan prosjektet er strukturert for langsiktig vedlikehold og utvidelse.

---

## Systemkomponenter

Systemet er inndelt i flere lag:

1. **App-lag (Flask)** – Starter applikasjonen, registrerer blueprints og initierer systemkomponenter.
2. **API og routes** – Flask blueprints håndterer ruting, autentisering og validering.
3. **Kjerne (core)** – `GarageController` styrer logikken for porter, timing, sensorer og reléer.
4. **Utils** – Reusable komponenter: pigpio, relay, sensorer, logger, auth, filhåndtering.
5. **Monitor** – Systemhelse og bakgrunnssjekker.
6. **Konfigurasjon** – JSON-baserte filer for all runtime-konfigurasjon.

---

## Fil- og mappestruktur

```
/app.py – Flask entrypoint
/config/ – Alle .json konfigurasjonsfiler
/core/ – GarageController, bootstrap, system
/utils/ – pigpio, logger, relay, sensor, auth
/routes/
└── api/ – Organiserte API-moduler (port, status, system, logg)
/monitor/ – Systemovervåking, pigpiod monitor
/docs/ – Dokumentasjon
/static/, /templates/ – Forberedt for frontend (ikke implementert ennå)

```

---

## Viktige moduler

### GarageController (`core/garage_controller.py`)
Hovedkontroller for:
- Reléaktivering
- Sensoravlesning og statusendringer
- Timingberegninger
- Logging
- Oppdatering av `config_system.json`

### RelayControl (`utils/relay_control.py`)
Henter GPIO-pinner fra `config_gpio.json`, og styrer releer med pigpio.

### SensorMonitor (`utils/sensor_monitor.py`)
- Konfigurerer sensorer
- Lytter på endringer via pigpio callbacks
- Sender tilstandsendringer til `GarageController`

### pigpio_manager
Delt singleton-løsning for `pigpio.pi()` – én instans per runtime, gjenbrukes overalt.

---

## Logging

Sentralisert logghåndtering via `GarageLogger`, med støtte for:
- `status.log`
- `errors.log`
- `activity.log`
- `timing.log`
- `bootstrap.log`

Støtter JSON-logging og konfigurasjon via `config_logging.json`.

---

## Konfigurasjon

Bruker `.json`-filer som lastes ved oppstart og valideres:
- `config_gpio.json`
- `config_system.json`
- `config_health.json`
- `config_logging.json`

Validering skjer i `core/bootstrap.py`.

---

## Helsetilstand

Periodisk overvåking av RPi:
- Temperatur, minne, disk, CPU-last, oppetid
- Sjekker mot terskler i `config_health.json`
- Logger og varsler ved avvik

Moduler: `monitor/system_monitor_task.py`, `utils/system_monitor.py`

---

## API-struktur

Alle ruter har `@token_required` og deles inn som:

- `/api/status` – Portstatus
- `/api/port/<port>/<action>` – Open/close/stop
- `/api/system/health` – pigpiod, sensor-monitor, GPIO
- `/api/system/rpi_status` – CPU, disk, minne, tid
- `/api/system/rpi_diagnostics` – terskelvurderinger
- `/api/logs/<type>` – Les loggfiler
- `/api/timing/<port>` – Timinghistorikk

---

## Fremtidige forbedringer

- Frontend-adminpanel
- Sanntidsstatus via WebSocket
- E-postvarsling på hendelser
- Historikkgrafer
- Automatisk konfigurering av systemd-tjenester
- Bedre testdekning (unit + integrasjon)

---

## Oppsummering

Prosjektet er strukturert for klar ansvarsdeling, enkel vedlikehold, og fremtidig utvidbarhet. Ved å holde alle konfigurasjoner i JSON og bruke veldefinerte moduler og API-ruter, sikres både robusthet og fleksibilitet.
