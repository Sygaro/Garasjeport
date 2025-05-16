
# Garasjeprosjekt – Utviklingslogg

🗓️ Dato: 2025-05-05  
🧑‍💻 Utviklingsøkt: Kveld

## ✅ Utført funksjonalitet

### Adminpanel /admin
- Fullstendig redesign av `admin.html`:
  - Dropdown-menyer for valg av GPIO-pinner til rele og sensorer
  - Brukte pinner vises som "i bruk" og er grået ut
  - Valgte pinner fra config.json er forhåndsvalgt
- Backend-validering (`app.py`):
  - Henter og sorterer tilgjengelige GPIO-pinner etter fysisk pin
  - Forhindrer at samme pin brukes flere ganger på én port
  - Lagrer gyldige valg tilbake til `config.json`
  - Viser flash-meldinger ved feil eller bekreftelse

### Backup og restore
- Ruter for:
  - Opprette ny backup (`/create-backup`)
  - Vise eksisterende (`/backup`)
  - Gjenopprette (`/restore/<filnavn>`)
- Bekreftet at dette fungerer

### GitHub
- Klargjort endringer for commit og push til GitHub
- Steg-for-steg dokumentert prosess for `git add`, `commit`, `push`
- Neste gang: opprette brancher for videre arbeid

## 🔜 Neste steg

- Kalibreringsfunksjon for porter
- Brukerhåndtering og roller
- Statistikk og visning
- Sanity check ved oppstart

## 🧠 Notat
- Oppdateringer gjort i `app.py` og `templates/admin.html`
- Husk å teste videre mot eksisterende GPIO-oppsett før neste utvidelse

