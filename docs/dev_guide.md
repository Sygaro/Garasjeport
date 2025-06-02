# Garasjeprosjekt Dev Guide

## 🌟 Mål

Bygge et robust, modulært og fremtidsrettet system for styring og overvåking av garasjeporter, med fleksibel konfigurasjon og sentralisert logging.

## ✅ Kjerneprinsipper

* **Modularitet**: Alt bygges i gjenbrukbare og logisk oppdelte moduler
* **Fleksibilitet**: Parametre og innstillinger hentes fra `.json` eller `config/*.py`, ikke hardkodet
* **Konsekvent stil**: Navn og struktur følger etablert standard
* **Feiltoleranse**: Fallback-logger, validering og defensive strategier
* **Logging**: Sentralisert system med loggnivåer, rotering og kategorier

---

## 📂 Struktur

| Katalog    | Formål                                          |
| ---------- | ----------------------------------------------- |
| `config/`  | Konfigurasjonsfiler (.json og .py)              |
| `utils/`   | Gjenbrukbare komponenter (f.eks. logging, GPIO) |
| `core/`    | Kjernearkitektur og oppstartslogikk             |
| `monitor/` | Bakgrunnsoppgaver og overvåkning                |
| `routes/`  | Flask-ruter/API                                 |
| `tests/`   | Tester og valideringer                          |
| `app.py`   | Applikasjonsstartpunkt                          |

---

## 🖊️ Logging

### Konfigurasjon

* `config_logging.json`: Inneholder logger pr. kategori:

```json
  "system": {
    "file_enabled": true,
    "console_enabled": true,
    "rotation_MB": 10,
    "max_backups_files": 5,
    "level": "DEBUG"
  }
```

* `log_categories.py`: Definerer gyldige kategorier som brukes i config og validering

### Komponenter

| Fil                    | Formål                                      |
| ---------------------- | ------------------------------------------- |
| `logger_manager.py`    | Oppretter logger-instans basert på config   |
| `unified_logger.py`    | Offentlig API: `get_logger(name, category)` |
| `logger_validation.py` | Statisk validering av logger i kildekode    |
| `log_config_loader.py` | Leser og pakker ut config-innstillinger     |
| `log_categories.py`    | Eneste autoritative liste over tillatte loggkategorier |
| `config_logging.json`  | Logger pr. kategori (`system`, `environment`, etc) definert med `file_enabled`, `console_enabled`, `rotation_MB`, `max_backups_files`, osv. |


### Bruk

```python
logger = get_logger("garage_controller", category="system")
logger.info("Systemet er startet")
```

* Feil loggkategori får fallback logger og feilmelding i `system.log`
* Logger kan skrive til flere targets (file, console)

---

## 🔄 Samarbeidsmodell

1. Jeg beskriver funksjonalitet eller feil
2. Du:

   * Forklarer løsningsstrategi
   * Foreslår struktur og evt. forbedringer
   * Lager kode i lerret med filnavn og kommentarer
3. Du tester og gir tilbakemelding
4. Iterasjon ved behov

---

## 🔍 Retningslinjer for utvikling

* Ikke hardkod parametre eller paths
* PEP8-vennlig, robust og skalerbar kode.
* All konfig skal leses fra `config/*.json` eller `config/*.py`
* Navn skal forklare formål og følge eksisterende stil
* Logger skal ha kategori og navn, og alltid bruke `get_logger()`
* Ikke bruk `print()`, bruk logging
* All ny kode skal inkludere logging der det er hensiktsmessig
* All logging foregår via det sentrrale loggsystemet under utils/logging
* Foreslå robuste forbedringer som følger etablert stil og arkitektur
* Unngå gjennbruk av kode med mindre det er hensiktsmessig og mer effektivt
* Avklar ting som er uavklart før du går videre
* Kode du genrerere skal inneholde kommentarer
* Alle filer skal starte med en kommentar med filnavnet
* Når jeg sender deg en .py eller .json fil skal du lese gjennom hele filen, ikke bare deler av den
* Når du gir meg kode skal du spesifisere om koden skal erstatte hele den eksistrende koden for den gjeldende filen, eller kun deler av koden
* Dersom det bare er deler av koden til en fil som skal endres må du gi tydelige instukser for hva og hvor koden skal settes inn og hva den ev. skal erstatte

---

## ✨ Eksempel på ny modul

Ved forespørsel om f.eks. ny sensorsjekk:

* Foreslår plassering (`monitor/sensor_checker.py`)
* Bruker `get_logger()` og logger til riktig kategori
* Parametre leses fra config
* Integrasjon skjer i `core/system.py` eller ny monitor-task

---

## ⚖️ Endringer

Alle endringer av:

* modulstruktur
* funksjonsnavn
* konfigfil-nøkler

... krever **avklaring og godkjenning**.

---

## 🚀 Neste steg

Jeg kan be deg om eksempelvis:

* ✏️ Generere ny modul eller komponent
* ⚠️ Finne og forklare bugs
* 🔄 Forbedre ytelse eller struktur
* 📄 Validere og loggføre kodebruk

Du skal alltid bruke lerret for å gi meg kode.