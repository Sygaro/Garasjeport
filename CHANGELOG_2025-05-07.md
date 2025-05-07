
# 📦 Endringer – Garasjeprosjektet

Dato: 2025-05-07  
Branch: `feature/logging-kalibrering`  
Commit: Automatisk kalibrering, logging og adminforbedringer

---

## ✅ Funksjonelle nyheter

### 🔧 Automatisk kalibrering
- Måling av åpnetid og lukketid basert på sensorsignal
- Tidsmåling logges og lagres i `config.json`
- Skille mellom automatisk og manuell kalibrering
- Timestamp for siste måling per port

### 🛠️ Adminpanel
- Viser kalibreringsverdier for hver port
- Manuell endring og lagring av verdier
- Nye knapper for å trigge måling av åpne-/lukketid
- Validering og visning per port

### 📜 Logger og systemhendelser
- Alle sensor- og kalibreringshendelser logges til `logs/events.log`
- Eventlogg vises i ny `/admin/log`-rute
- Tabell med:
  - Tidspunkt (delt opp i klokkeslett + dato)
  - Type
  - Port
  - Melding
  - Tilleggsdata (JSON)
- Filtrering med dropdown-meny:
  - Filtrer på `type` og `port`
  - Klient-side JavaScript filtrering
- CSS-stil lagt til for tydelig tabellstruktur

---

## 🧹 Rydding og forbedringer
- `app.py` er ryddet: duplikate ruter fjernet, alle funksjoner kommentert
- `base.html` linker nå til loggvisning og kalibrering
- Rute `/stats` og `stats.html` placeholder lagt til

---

## 🔄 Anbefaling for videre arbeid

- Start ny branch for `feature/stats`
- Lagre nye moduler trinnvis
- Sørg for full test på fysisk Pi når sensorer er koblet til
