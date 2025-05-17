# Dokumentasjon for garage_controller.py

## 📌 Formål
`garage_controller.py` er ansvarlig for all fysisk interaksjon med garasjeportene via GPIO-pinner. Dette inkluderer:
- Aktivering av reléutgang for å åpne/lukke porter
- Avlesning av sensorer for portstatus
- Håndtering av sanntidshendelser med GPIO (via add_event_detect)
- Kalibrering og statusvurdering basert på sensordata
- Opprettholdelse av modularitet og isolasjon fra frontend og Flask-logikk

## 🔧 Funksjoner og deres hensikt
| Funksjon | Beskrivelse |
|----------|-------------|
| `__init__(self, config)` | Leser GPIO-konfig fra `config.json`, setter opp rele- og sensorpinner. Aktiverer GPIO-interrupts. |
| `send_pulse(self, port)` | Sender en kort puls til portens reléutgang. Brukes til tvungen aktivering. |
| `send_pulse_raw(self, port)` | Lavnivåfunksjon for puls uten sjekker. Brukes ved ukjent status. |
| `try_send_pulse(self, port, action="open")` | Kontrollerer sensorstatus før puls sendes. Logger, returnerer meldinger og resultat. |
| `get_port_status(self, port)` | Leser status fra begge sensorer og returnerer 'åpen', 'lukket', 'ukjent' eller 'sensorfeil'. |
| `read_sensor(self, port, position)` | Leser én spesifikk sensorpinne og returnerer høy/lav. |
| `update_config(self, new_config)` | Dynamisk oppdatering av GPIO-konfig og gjenoppsett av pinner. |
| `cleanup(self)` | Rydder opp GPIO-pinner ved avslutning. Kalles ved atexit. |

## 🔗 Relasjon til config.json
`garage_controller.py` forventer følgende felter i `config.json`:
- `relay_pins`: `{ port1: BCM_nummer, port2: BCM_nummer }`
- `sensor_pins`: `{ port1: { open: BCM, closed: BCM }, port2: { ... } }`
- Disse verdiene hentes ved oppstart og brukes for all GPIO-logikk.

## 🔄 Logikk for åpning/lukking av porter
1. Status leses med `get_port_status()` fra sensorene.
2. Hvis status == ønsket posisjon: **ingen puls sendes**.
3. Hvis status == `ukjent`: bruker må bekrefte handling.
4. Hvis status == `sensorfeil`: handling blokkeres.
5. Hvis status er gyldig, sendes **puls på rele**: `GPIO.output(pin, LOW)` → vent → `GPIO.output(pin, HIGH)`.
6. Det logges alltid med tidspunkt og port.

## 📏 Kalibreringslogikk
1. Sjekk startstatus: må være `lukket` for åpne-kalibrering, `åpen` for lukke-kalibrering.
2. Hvis ikke, spør bruker om vi skal lukke/åpne port først.
3. Kalibreringsrutine:
   - Send puls → start tidtaker
   - Vent til første sensor endres (lukket → inaktiv)
   - Start del 2: mål tid til neste sensor (åpen → aktiv)
   - Logg: delay + overgangstid + total tid
   - Lagre i `config.json` under `calibration`-seksjon

## ⚙️ Tekniske krav og hensyn
- **Ingen polling**: Bruk `GPIO.add_event_detect()`
- **Debounce**: Bruk `bouncetime=200`
- **Fail-safe**: Ingen handling ved sensorfeil eller ukjent port
- **Trådsikkerhet**: Unngå deling av rå GPIO-modifikasjoner uten kontroll
- **Kalibreringslogger**: Lagres i `logs/calibration_history.log`
- **Eventlogger**: Åpne/lukke-aksjoner logges i `logs/events.log`
- **Status-synkronisering**: WebSocket oppdaterer status live i frontend

## 🧩 Sensor + Rele-kobling
- Sensorer kobles til GND (bruk `PUD_UP` internt)
- Sensor aktiv = GPIO input LOW
- Når rele aktiveres: `GPIO.output(pin, GPIO.LOW)` → port beveger seg

## 🔔 Kommunikasjon og varsler
- `flash()` i Flask brukes til å varsle bruker
- WebSocket kan sende statusoppdatering til frontend ved sensor-endringer

## 🧹 Rydding
- Kall `garage.cleanup()` ved avslutning for å frigjøre GPIO