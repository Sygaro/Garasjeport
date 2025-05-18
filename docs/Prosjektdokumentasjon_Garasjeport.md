# Garasjeprosjekt – Filoversikt og Dokumentasjon

## 1. Prosjektoversikt
Dette dokumentet gir oversikt over filstruktur, funksjoner, og anbefalt opprydding for garasjeprosjektet.

## 2. Hovedfiler og deres funksjon
- **app.py**: Hovedfil for Flask-applikasjonen. Inneholder alle ruter og konfigurasjon.
- **garage_controller.py**: Kontrollerer relé, sensorer og GPIO – sentral portstyringslogikk.
- **calibration.py**: Måler og kalibrerer åpne/lukke-tider, samt lagrer disse.
- **calibration_logger.py**: Logger kalibreringstider i en separat loggfil.
- **logger.py**: Konfigurerer logghåndtering og loggnivå.
- **event_log.py**: Logger hendelser til events.log i JSON-format.
- **config.py**: Lasting og lagring av config.json, med system- og portinnstillinger.
- **auth.py**: Enkel autentisering med brukernavn/passord.
- **log_utils.py**: Behandler og filtrerer loggvisning.
- **backup.py**: Trolig utdatert – backup-funksjoner flyttet til app.py.
- **requirements.txt**: Liste over pip-pakker og avhengigheter for prosjektet.
- **garage_controller.py.medFeil**: Utdatert versjon med feil – kan slettes.

## 3. HTML-maler i `templates/`
Disse filene utgjør brukergrensesnittet og er bygget på base.html. Flere bruker Bootstrap og inneholder interaktive funksjoner som Socket.IO og filtrering.

## 4. Oversikt over Python-funksjoner
Se egen tabell med oversikt over funksjoner og hvor de brukes.

## 5. Anbefalte filer å rydde bort
Filer som bør slettes eller flyttes for å rydde i prosjektet:
- `garage_controller.py.medFeil`
- `log_old.html`
- `backup.py`