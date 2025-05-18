# Dokumentasjon for calibration.py

## 📌 Formål
`calibration.py` håndterer måling og kalibrering av portenes åpne- og lukketider. Den benytter sensoravlesninger og presis timing for å fastslå hvor lang tid en port bruker på å åpne/lukke seg.

## 🔧 Funksjoner og deres hensikt
| Funksjon | Beskrivelse |
|----------|-------------|
| `calibrate_open(port, timeout=60)` | Starter kalibrering av åpnetid. Måler tid fra lukket sensor slipper → åpen sensor aktiveres. |
| `calibrate_close(port, timeout=60)` | Starter kalibrering av lukketid. Måler tid fra åpen sensor slipper → lukket sensor aktiveres. |
| `calibrate(port, action, timeout=60)` | Felleslogikk brukt av open/close for å måle rele delay, overgangstid og total varighet. |
| `save_calibration(port, open_time=None, close_time=None, source='auto')` | Lagrer kalibrerte tider i `config.json`, og registrerer om verdien er manuell eller automatisk. |

## 🔗 Relasjon til config.json
- Kalibreringstider lagres under `config['calibration'][port]` med nøkler: `open_time`, `close_time`, `source`, `timestamp`
- `backup_retention_days` brukes i backup-håndtering

## 🧠 Logikk for kalibrering
1. Kontroller at port er i riktig startposisjon (lukket/åpen)
2. Hvis ikke, tilby automatisk bevegelse først
3. Send puls til portens rele
4. Start tidtaking:
   - Del 1: Mål tid til første sensor deaktiveres (f.eks. lukket slipper)
   - Del 2: Mål tid til neste sensor aktiveres (f.eks. åpen registreres)
5. Summer `rele_delay + sensor_to_sensor` = total åpne-/lukketid
6. Lagre resultat med `save_calibration()` og logg i `calibration_history.log`

## 📦 Logging
- Funksjonen `log_calibration_measurement()` i `calibration_logger.py` lagrer:
  - port, type, rele delay, sensor overgang, total tid, timestamp
- Logger lagres i `logs/calibration_history.log`

## ⚙️ Tekniske krav og hensyn
- **Ingen polling**: bygger på `GPIO.add_event_detect()` via `garage_controller`
- **Fail-safe**: Timeout etter 60 sekunder
- **Brukerstyrt bevegelse**: Ved ukjent eller feil status må bruker bekrefte start av motor
- **Kildemerking**: Det skilles på manuell og automatisk kalibrering (`source`)
- **Avvikshåndtering**: Hvis port ikke når ønsket posisjon i tide, logges feil og None returneres

## 🔗 Avhengigheter
- `garage_controller.garage` må injiseres før bruk (deles med app.py)
- Bruker `log_event` for hendelseslogging
- Bruker `load_config` og `save_config` fra config-modul