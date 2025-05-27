# Configuration

Dette dokumentet forklarer strukturen og bruken av konfigurasjonsfilene i garasjeportprosjektet. Konfigurasjonene er modulære og ligger under `config/`-mappen. Alle baner og filnavn hentes fra `config_paths.py` for å sikre fleksibilitet og vedlikeholdbarhet.

---

## Innhold

- [Konfigurasjonsoversikt](#konfigurasjonsoversikt)
- [config_gpio.json](#config_gpiojson)
- [config_system.json](#config_systemjson)
- [config_logging.json](#config_loggingjson)
- [config_auth.json](#config_authjson)
- [config_health.json](#config_healthjson)
- [config_timing.json](#config_timingjson)
- [Validering](#validering)

---

## Konfigurasjonsoversikt

| Filnavn               | Beskrivelse                                               |
|-----------------------|-----------------------------------------------------------|
| config_gpio.json      | GPIO-konfigurasjon for releer og sensorer                |
| config_system.json    | Lagring av status, timing, og historiske målinger        |
| config_logging.json   | Loggingformat, rotasjon, og maks størrelse               |
| config_auth.json      | Autentiseringsnøkler for API                              |
| config_health.json    | Systemhelsesjekk og varslingsterskler                    |
| config_timing.json    | Standard timingverdier for fallback                      |

---

## config_gpio.json

Konfigurerer GPIO-pins og oppførsel for releer og sensorer.

```json
{
  "relay_pins": {
    "port1": 14,
    "port2": 15
  },
  "sensor_pins": {
    "port1": {
      "open": 23,
      "closed": 24
    },
    "port2": {
      "open": 20,
      "closed": 21
    }
  },
  "relay_config": {
    "active_state": 0,
    "pulse_duration": 0.4
  },
  "sensor_config": {
    "pull": "up",
    "active_state": 0
  }
}
```

#### config_system.json
Systemets runtime-data – f.eks. status, timingmålinger og siste endringer.

```
{
  "port1": {
    "status": "closed",
    "status_timestamp": "2025-05-26 10:32:12",
    "timing": {
      "open": {
        "last": 27.5,
        "avg": 27.3,
        "t0": 0.6,
        "t1": 26.9,
        "t2": 27.5,
        "history": [27.2, 27.4, 27.3]
      },
      "close": { ... }
    }
  },
  "port2": { ... }
}
```

#### config_logging.json
Styrer logger og rotasjon.

```
{
  "rotation_days": 7,
  "max_file_size_mb": 5,
  "backup_count": 3,
  "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
}
```

#### config_auth.json
Enkel token-basert autentisering for API-ruter.

```
{
  "api_token": "super_secure_token"
}

```

#### config_health.json
Definerer terskler for RPi-status og varslinger.

```
{
  "thresholds": {
    "cpu_temp_max": 70,
    "disk_usage_max_percent": 85,
    "memory_usage_max_percent": 80,
    "min_free_disk_gb": 1.0,
    "min_free_memory_mb": 100
  },
  "alerts": {
    "enabled": true,
    "interval_minutes": 15,
    "repeat_max": 3
  }
}
```

#### config_timing.json
Fallback-tider dersom historiske målinger ikke finnes.

```
{
  "timing_config": {
    "default_open_time": 28.0,
    "default_close_time": 28.0,
    "fail_margin_status_change": 3
  }
}
```

#### Validering
Ved oppstart valideres alle konfigurasjoner via core/bootstrap.py. Hver modul har sin egen valideringslogikk som kontrollerer typer, manglende verdier og datatyper.

Eksempel på valideringskall:

```
from utils.config_loader import load_config
from core.bootstrap import validate_config_gpio

config = load_config(paths.CONFIG_GPIO_PATH)
validate_config_gpio(config)
```

### Oppsummering
Konfigurasjonene er nøkkelen til fleksibilitet og robusthet i garasjesystemet. Endringer i JSON-filer vil automatisk påvirke hvordan systemet oppfører seg – uten behov for å endre Python-kode.
