# Garasjeportstyring med Raspberry Pi

Dette prosjektet gir full kontroll over to garasjeporter via Raspberry Pi, med støtte for statusovervåkning, reléstyring, tidtaking, logging og API-integrasjon.

## 🚀 Funksjoner

- Fjernstyring av porter via webgrensesnitt og API
- Deteksjon av portstatus (åpen, lukket, bevegelse, sensorfeil)
- Automatisk tidsmåling ved åpning/lukking
- Logging til fil (status, aktivitet, feil, timing)
- Konfigurasjon via `.json`-filer
- Autentisering (API-token og webhooks)
- Støtte for Homey og andre smarthusintegrasjoner
- Fremtidig UI via adminpanel

---

## 📦 Installasjon

### 1. Koble opp maskinvare

- **Raspberry Pi 5** for utvikling / **Pi Zero 2 W** for produksjon
- Koble til 2-kanals relémodul og 2 reed-sensorer per port
- Sensorene kobles med GND og aktiv pull-up
- Relé styres med kortvarige impulser

### 2. Klon repoet

```bash
git clone --branch feature/v1.05_frontend https://github.com/Sygaro/Garasjeport
cd garasjeport
```
### 3. Opprett virtuelt miljø og installer avhengigheter

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
####  Installer lgpio for GPIO-styring.

```bash
sudo apt install python3-lgpio
```
