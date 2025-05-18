# 📦 Dokumentasjon: Garasjeportstyring med Raspberry Pi

## 🎯 Hensikt med systemet

### Overordnet
Garasjeportsystemet er utviklet for å tilby lokal, sikker og brukervennlig kontroll av én eller flere garasjeporter via Raspberry Pi. Systemet gir brukeren tilgang via webgrensesnitt og tilbyr API-integrasjon for smarthusløsninger som Homey Pro.

### Detaljert
Systemet gir:
- Kontroll for åpning og lukking av porter
- Sanntidsstatus med sensoravlesning
- Automatisk og manuell kalibrering
- Loggføring av alle hendelser
- Konfigurasjonsgrensesnitt for porter og systeminnstillinger
- Visuelle dashbord og grafisk presentasjon av portdata

## 🧾 Krav og prinsipper

- ❌ **Ikke polling**: Systemet må bruke `GPIO.add_event_detect()` for å registrere endringer. Dette gir lavere ressursbruk og bedre respons.
- ✅ **gpiod-bibliotek** skal erstatte `RPi.GPIO` pga. stabilitetsproblemer på nyere Raspberry Pi-modeller.
- 🧩 **Modulært design**: Kodebasen er delt i tydelige moduler: `garage_controller`, `calibration`, `event_log`, `config` osv.
- 🧠 **Live status**: Bruker WebSockets for å oppdatere portstatus i sanntid.
- 🔐 **Autentisering**: Enkel brukerbeskyttelse og sesjonskontroll
- 🔁 **Failsafe og feilrapportering**: Feilhåndtering og logging i alle rutiner
- 📈 **Logging og statistikk**: Hendelser logges som JSONL, portåpninger telles og målinger arkiveres for historikk.

## 🧠 Overordnet logikk

### Porter
- Hver port styres via ett relé (GPIO OUT) og to sensorer (GPIO IN)
- Sensor 1: registrerer når port er **åpen**
- Sensor 2: registrerer når port er **lukket**
- Tilstand bestemmes basert på sensorene:
  - Begge sensorer = 0 → port beveger seg
  - Lukket = 1 og åpen = 0 → port lukket
  - Åpen = 1 og lukket = 0 → port åpen
  - Begge = 1 → **feil** (defekt sensor/kortslutning)

### Styring
- Brukeren kan åpne/lukke porter via knapp, API eller Homey.
- Før en puls sendes til releet:
  - Status sjekkes
  - Ved ukjent status spørres bruker om bekreftelse
  - Sensorfeil blokkerer handling

### Kalibrering
- Systemet måler hvor lang tid en port bruker på å åpne/lukke seg
- Målingen inkluderer:
  1. Rele delay (fra puls til første sensor skifter)
  2. Sensor-til-sensor tid (fra første til andre sensor)
  3. Total tid = rele_delay + sensor_to_sensor
- Både åpne- og lukketid loggføres og lagres i config.json
- Manuell kalibrering støttes også

## 🔬 Detaljert logikk

### Åpning/lukking
1. Bruker klikker «åpne/lukke»
2. `try_send_pulse()` sjekker status
3. Hvis status er kjent og gyldig → puls sendes til rele
4. Hvis ukjent → vis bekreftelsesside
5. Etter puls, `GPIO.add_event_detect()` fanger endring og oppdaterer status via SocketIO

### Kalibrering
1. Portens starttilstand bekreftes (lukket for åpning, åpen for lukking)
2. Releet aktiveres
3. Timer starter når første sensor endrer seg
4. Timer stopper når neste sensor endrer seg
5. Resultat loggføres i `calibration_history.log`
6. Kalibrerte tider oppdateres i config

### Sensorlesing
- Bruker `GPIO.add_event_detect()` for å unngå polling
- Sensorstatus leses kontinuerlig og oppdateres live
- Sensorer er koblet til GND (pud_up i kode)

### Logging
- Logger deles i:
  - `events.log`: åpning, lukking, kalibrering, feil
  - `calibration_history.log`: måleverdier, detaljer per port
- Format: JSONL for enkel analyse og gjenbruk

### Sikkerhet og feilhåndtering
- Alle ruter krever innlogging hvis `require_login = true` i config
- Session timeout med justerbar varighet
- Maksimaltid for portåpning/lukking kan angis
- Sensorfeil eller timeout logges og varsles

## 📋 Anbefalt videreutvikling
- [ ] Full støtte for `gpiod`
- [ ] GUI for kalibreringshistorikk
- [ ] Temperatur/fuktighetslogging per måling
- [ ] API for statistikk og portkontroll
- [ ] Automatisk varsel ved sensoravvik eller treghet