# API – Garasjeportprosjektet

Alle API-endepunkter bruker `/api` som URL-prefix og krever gyldig token (via `@token_required`-dekoren).

---

## Autentisering

Alle API-kall må inkludere en gyldig token i header:

```
Authorization: Bearer <ditt_token>
```


---

## Status

| Endpoint                          | Metode | Beskrivelse                     |
|----------------------------------|--------|---------------------------------|
| `/api/status`                    | GET    | Henter status for alle porter  |
| `/api/status/<port>`             | GET    | Henter status for én port      |

---

## Portkontroll

| Endpoint                            | Metode | Beskrivelse                     |
|------------------------------------|--------|---------------------------------|
| `/api/port/<port>/open`            | POST   | Åpner port                      |
| `/api/port/<port>/close`           | POST   | Lukker port                     |
| `/api/port/<port>/stop`            | POST   | Stopper port                    |

---

## Timing

| Endpoint                          | Metode | Beskrivelse                     |
|----------------------------------|--------|---------------------------------|
| `/api/timing/<port>`             | GET    | Timinghistorikk for én port    |
| `/api/timing/all`                | GET    | Timingdata for alle porter     |

---

## System

| Endpoint                             | Metode | Beskrivelse                                     |
|-------------------------------------|--------|-------------------------------------------------|
| `/api/system/health`                | GET    | Sjekker pigpiod og sensor-monitor              |
| `/api/system/rpi_status`            | GET    | RPi status: CPU, disk, oppetid, temperatur     |
| `/api/system/rpi_diagnostics`       | GET    | Forenklet helsesjekk med terskelvarsler        |
| `/api/system/bootstrap_status`      | GET    | Status fra systemstart                         |

---

## Logging

| Endpoint                          | Metode | Beskrivelse                                |
|----------------------------------|--------|--------------------------------------------|
| `/api/logs`                      | GET    | Liste over tilgjengelige loggtyper         |
| `/api/logs/<logtype>?lines=100` | GET    | Returnerer siste X linjer av loggfil       |
| `/api/log`                       | GET    | Siste linjer fra aktivitetsloggen          |

---

## Konfigurasjon

| Endpoint                              | Metode | Beskrivelse                              |
|--------------------------------------|--------|------------------------------------------|
| `/api/config/<module>`               | GET    | Returnerer innhold fra en konfigfil      |
| `/api/config/<module>`               | PUT    | Oppdaterer innhold i en konfigfil        |

---

## Versjon

| Endpoint                              | Metode | Beskrivelse                              |
|--------------------------------------|--------|------------------------------------------|
| `/api/system/version_report`         | POST   | Mottar frontend-versjon fra klient       |

---

### Feilmeldinger

- `401 Unauthorized` – mangler token
- `400 Bad Request` – ugyldige parametere
- `404 Not Found` – rute eller ressurs finnes ikke
- `500 Internal Server Error` – noe gikk galt i backend

---

## Eksempel

```bash
curl -X POST http://<rpi_ip>:5000/api/port/port1/open \
  -H "Authorization: Bearer <token>"
```

---

### `docs/logging.md`


# Logging – Garasjeportprosjektet

Logging er en sentral del av systemet og gir oversikt over statusendringer, feil, hendelser og timingmålinger. Logging er modulær og konfigurerbar via `config_logging.json`.

---

## Loggtyper

| Filnavn           | Beskrivelse                                       |
|-------------------|---------------------------------------------------|
| `status.log`      | Statusendringer og systembeskjeder                |
| `errors.log`      | Kritiske feil, exceptions, feil ved konfigurasjon |
| `activity.log`    | Hendelser som API-kall, brukerhandlinger          |
| `timing.log`      | Timingmålinger og analyser av portbevegelse       |
| `bootstrap.log`   | Oppstart og validering av systemet                |

---

## Logging via `GarageLogger`

Alle logger håndteres av `GarageLogger`-klassen.

```python
logger.log_status("controller", "Statusmelding")
logger.log_error("sensor", "Feilmelding")
logger.log_action(port="port1", action="open", source="api")
logger.log_timing("port1", {"direction": "open", "t0": 1.2, "t2": 28.1})
```

## Formater
Alle logger er tekstbaserte, med strukturert format:

```
2025-05-26 13:45:12 [INFO] controller: Statusmelding
2025-05-26 13:45:14 [ERROR] sensor: Feilmelding
2025-05-26 13:45:16 [ACTION] port1: Action=open, source=api
```

## Konfigurasjon (eksempel)

```
{
  "log_levels": {
    "status": "INFO",
    "errors": "ERROR",
    "timing": "INFO",
    "activity": "DEBUG",
    "bootstrap": "INFO"
  },
  "max_log_size_kb": 200,
  "backup_count": 3
}

```

## Logg-API

`/api/logs` – liste over loggtyper

`/api/logs/status?lines=50` – les siste 50 linjer

`/api/log` – alias for aktivitetsloggen


## Fremtidige muligheter

- Støtte for JSON-format
- E-postvarsling ved feil
- Automatisk arkivering eller rotasjon