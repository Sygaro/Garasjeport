# Sensor-dokumentasjon

## 🔧 Oversikt over Garasjeport-sensorer

### 💡 Sensor-type: Magnetisk Reed Switch
Systemet bruker magnetiske reed-sensorer til å registrere portens posisjon (helt åpen / helt lukket).

---

## 1. 🛠️ Maskinvare (Hardware)

| Egenskap         | Verdi                     |
|------------------|---------------------------|
| Type             | Magnetisk reed-bryter     |
| Antall per port  | 2 stk                     |
| Tilkobling       | 3-pinners (NO, NC, GND)   |
| Monteringsmetode | Faste montert med magnet  |

**✅ For hver port:**
- 1 sensor i “helt lukket” posisjon
- 1 sensor i “helt åpen” posisjon

---

## 2. 🔌 Elektrisk tilkobling

### ✨ Typisk koblingsskjema (NO-type):

| Pin   | Beskrivelse         | Kobles til        |
|--------|----------------------|-------------------|
| NC     | Normally Closed      | Ikke brukt        |
| NO     | Normally Open        | GPIO-pinne        |
| GND    | Jord (ground)        | GND på Raspberry Pi |

> ⚠️ Sensoren er aktiv når magneten er nær og GPIO trekkes til GND (lavt signal, 0).

---

## 3. ⚙️ Funksjon i systemet

### 📘 Sensorstatus-logikk

```python
open_active = (lgpio.gpio_read(self.chip, open_pin) == active_state)
closed_active = (lgpio.gpio_read(self.chip, closed_pin) == active_state)

if open_active and not closed_active:
    status = "open"
elif closed_active and not open_active:
    status = "closed"
elif not open_active and not closed_active:
    status = "moving"
elif open_active and closed_active:
    status = "sensor_error"
```

### 🔄 Bruksområder
| Funksjon             | Bruker sensor? | Forklaring                             |
| -------------------- | -------------- | -------------------------------------- |
| Statusavlesning      | ✅              | Leser aktiv sensor for portstatus      |
| Tidtaking            | ✅              | Brukes i åpne/lukke-timing             |
| Feilregistrering     | ✅              | Hvis ingen sensor endres etter timeout |
| Manuell intervensjon | ✅              | Fanger opp “manuell” portbruk          |

## 4. 🚀 Konfigurasjon i .json
Defineres i config_gpio.json:

```python

"sensor_pins": {
  "port1": { "open": 17, "closed": 27 },
  "port2": { "open": 22, "closed": 23 }
},
"sensor_config": {
  "pull": "up",
  "active_state": 0
}
```


| Felt           | Beskrivelse                             |
| -------------- | --------------------------------------- |
| `pull`         | "up" = intern pull-up-motstand aktivert |
| `active_state` | 0 = aktiv når GPIO trekkes lav          |


## 5. 🔍 Oppsummering

| Punkt           | Verdi                                      |
| --------------- | ------------------------------------------ |
| Sensor-type     | Magnetisk reed switch                      |
| Antall per port | 2                                          |
| Aktiv tilstand  | GPIO = 0                                   |
| Konfigurerbart  | Ja, via config\_gpio.json                  |
| Bruksområder    | Status, tidtaking, feil, manuell deteksjon |


