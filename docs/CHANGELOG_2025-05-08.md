Endringer i Garasjeport-prosjektet (Mai 2025)
Denne branchen inneholder alle forbedringer og oppdateringer som ble gjort i samarbeid med ChatGPT.

🔀 Struktur og versjonskontroll
Endringer lagt til i en egen branch: oppgradering-chatgpt-mai2025

✅ Hovedforbedringer
🔒 Innlogging med støtte for av/på via config.json
Ny rute: /login og /logout

Brukernavn og passord leses fra config.json:

json
Kopier
Rediger
"auth": {
  "username": "admin",
  "password": "1234"
},
"require_login": true
Funksjon login_required_if_enabled beskytter ruter bare dersom require_login er satt til true

🌙 Lys-/mørk-modus
Knapp i navigasjonsmeny for å veksle mellom lys/mørk tema

Bruker localStorage for å huske valgt modus

Automatisk stilendring på body, bakgrunn og tekst

🧭 Admin-forbedringer
Ny layout i admin.html: porter vises side-om-side i to kolonner

Ryddigere konfigurasjons- og kalibreringskort

Dropdowns deaktiverer brukte GPIO-pinner for å forhindre feil

📈 Statistikkvisning (/stats)
Bruker Chart.js (via CDN)

Viser dummydata for portåpninger gjennom uken

Klar for å kobles mot reelle loggdata senere

📜 Loggvisning (/admin/log)
Filtrering etter:

Type (error, info, calibration, etc.)

Port

Datoområde (fra/til med kalender)

CSV-eksport av synlige rader

Modal-popup for detaljerte loggdata (via 🔍-knapp)

Fargekoder for port og kritiske meldinger

💾 Backup-siden (/backup)
Renere oversikt over backup-filer

Handlingsknapper:

🧾 Vis innhold

⬇️ Last ned fil

♻️ Gjenopprett backup (med bekreftelse)

🧠 Diverse forbedringer
@context_processor feilrettet: fjernet @login_required_if_enabled som forårsaket TypeError

Feil i config.json ved bruk av enkeltsitater ble oppdaget og håndtert

Navigasjonsmeny lagt til med lenker:

Hjem, Admin, Logg, Statistikk, Backup, Logg inn/ut

Tekst på forsiden (Oversikt over porter...) får riktig kontrast i mørk modus

📁 Nye og endrede filer
templates/login.html – ny side for innlogging

Oppdatert:

app.py

base.html (navigasjon + nattmodus)

admin.html (layout + kalibrering)

log.html (filtrering, modal, CSV)

stats.html (diagram)

backup.html (nytt utseende)

config.json (nytt felt auth og require_login)

💡 Forslag til videre utvikling
Flere brukere og roller (admin / readonly)

Automatisk daglig backup

Live-status med WebSocket eller AJAX

E-postvarsling ved feil
