# 📄 Systembeskrivelse: Garasjeporter uten styringssystem

## 📌 Formål
Dette dokumentet forklarer hvordan garasjeportene fungerer uten noen tilkoblet styringsenhet (Raspberry Pi, releer, sensorer osv.). Det danner grunnlaget for hvorfor vi bygger et nytt system og hvilke svakheter det skal løse.

---

## ⚙️ Fysisk oppsett

Hver garasjeport styres av en **motorisert portåpner** som:
- Aktiveres via **impulsbryter**
- Har fast kjøretid for åpning/lukking (ca. X sekunder)
- Stopper automatisk ved full åpning eller lukking (basert på motorens innebygde grensebrytere)
- **Har ingen elektronisk statusovervåkning**

Portåpneren responderer på en **kortslutning** mellom to innganger (fra bryter eller rele). Ingen ekstra intelligens er implementert.

---

## 🔘 Impulsbryterens funksjon

Bryteren er en enkel **trykk-knapp** koblet direkte til portens kontrollenhet:

| Trykk | Handling |
|-------|----------|
| 1.    | Starter bevegelse (åpne eller lukke) |
| 2.    | Stopper motor (uansett retning)     |
| 3.    | Starter motsatt retning             |

> Viktig: Porten har **ingen statuslogikk**. Den husker ikke sin tilstand og antar alltid at brukeren vet hva som skjer.

---

## 🔄 Manuell sekvenslogikk

| Nåværende status | Impuls handling | Resultat |
|------------------|------------------|----------|
| Lukket           | Impuls           | Port begynner å åpne |
| Åpen             | Impuls           | Port begynner å lukke |
| I bevegelse      | Impuls           | Motoren stopper       |
| Halvåpen         | Impuls           | Motor starter motsatt vei |

---

## 🧲 Reed-sensorer (eksternt)

Du har manuelt installert to reed-sensorer per port:
- En for "port helt åpen"
- En for "port helt lukket"

Disse gir **digitalt signal (på/av)** til vårt styringssystem og er:
- Koblet til GPIO på Raspberry Pi
- Ikke integrert med selve motoren
- Brukes for **statusavlesning**

---

## 🚫 Begrensninger i eksisterende løsning

- ❌ Ingen mulighet for å vite portens status
- ❌ Ingen historikk/logging
- ❌ Ingen feildeteksjon
- ❌ Ingen fjernstyring
- ❌ Ingen sikkerhetsmekanismer

---

## 🧠 Hvorfor dette er viktig for vårt system

Denne oppførselen forklarer hvorfor vårt prosjekt må inneholde:
- Sensoravlesning med statuslogikk
- Pulsbasert styring med logging
- Sikker logikk for å detektere bevegelse, feil og stopp
- API for eksterne systemer (f.eks. Homey)
- Webgrensesnitt for administrasjon og manuell styring
- Robust system for **å unngå feilpuls, overstyring og statusfeil**

---

## 🧩 Sammendrag

Det eksisterende systemet er funksjonelt, men "dumt":
- Det vet ingenting om hvor porten er
- Det gir ikke tilbakemelding
- Det tilbyr ingen fjernstyring eller integrasjon

Vårt system bygger **intelligens og kontroll** rundt denne eksisterende mekaniske funksjonaliteten uten å erstatte den.

---
