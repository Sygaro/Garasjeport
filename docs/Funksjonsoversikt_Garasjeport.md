# Funksjonsoversikt – Garasjeprosjektet

## app.py

| Funksjon | Beskrivelse |
|----------|-------------|
| `session_timeout_check` | Sjekker om brukeren har vært inaktiv og logger ut ved timeout. |
| `login` | Håndterer innlogging med brukernavn og passord. |
| `logout` | Logger ut brukeren og rydder sesjonen. |
| `admin` | Viser og oppdaterer systeminnstillinger og GPIO-konfigurasjon. |
| `admin_ports` | Håndterer oppdatering av porter og kalibrering. |
| `admin_backup` | Lister og vedlikeholder backupfiler. |
| `restore_backup` | Gjenoppretter tidligere backup. |
| `compare_backups` | Sammenligner to backupfiler og viser forskjeller. |
| `vis_eventlogg` | Viser hendelseslogg fra logs/events.log. |
| `port_stats` | Viser portstatus og statistikk for bruk. |
| `open_port` | Forsøker å åpne port, basert på status. |
| `close_port` | Forsøker å lukke port, basert på status. |
| `force_port_action` | Tvinger åpne/lukke-signal til rele uansett status. |

## garage_controller.py

| Funksjon | Beskrivelse |
|----------|-------------|
| `__init__` | Initialiserer GPIO, releer og sensorer. |
| `send_pulse` | Sender kort puls til releet. |
| `send_pulse_raw` | Sender puls til rele uavhengig av status. |
| `try_send_pulse` | Sjekker status og sender puls om nødvendig. |
| `get_port_status` | Returnerer status basert på sensorer. |
| `read_sensor` | Leser en gitt sensor (open/closed). |

## calibration.py

| Funksjon | Beskrivelse |
|----------|-------------|
| `calibrate_open` | Måler åpnetid inkludert rele-delay og sensor til sensor. |
| `calibrate_close` | Måler lukketid inkludert rele-delay og sensor til sensor. |
| `calibrate` | Felles logikk for åpne/lukke basert på sensorstatus. |
| `save_calibration` | Lagrer målt kalibreringsdata i config. |

## calibration_logger.py

| Funksjon | Beskrivelse |
|----------|-------------|
| `log_calibration_measurement` | Logger kalibrering med detaljer til loggfil. |
