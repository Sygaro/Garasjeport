# Systembeskrivelse

Dette prosjektet er et styringssystem for garasjeporter basert på Raspberry Pi. Det gir mulighet for fjernstyring, statusovervåkning og logging av porter via webgrensesnitt og API. Systemet er designet for fleksibilitet og sikkerhet, og støtter manuell styring samt integrasjon med Homey Pro og andre smarthusløsninger.

## Hensikt

- **Automatisert styring av garasjeporter**
- **Fjernstyring via API/Web UI**
- **Tidsmåling og logging av portbevegelse**
- **Avansert feildeteksjon og sensorstatus**
- **Integrasjon med tredjeparts systemer**

## Hvordan garasjeportene fungerer uten systemet

- Hver port har en impulsbryter koblet til portmotoren
- En kortslutning mellom to pinner gir en **impuls** som starter eller stopper motoren
- Motoren åpner eller lukker porten fullstendig basert på nåværende posisjon
- Hvis impuls sendes mens motoren kjører, **stanser motoren**
- Ved ny impuls starter motoren i motsatt retning
- Portene har ikke innebygget posisjonslogikk – det er styringssystemets ansvar

## Hovedfunksjoner i systemet

- **GPIO-styring** for to porter med relé
- **Sensorstatus**: Åpen, lukket, bevegelse, sensorfeil
- **Rele-logikk**: konfigurerbar høy/lav puls
- **Tidtaking av åpne/lukke-prosesser**
- **Timeout- og feilmarginer**
- **Logging i fire separate filer**
- **Støtte for stopp-funksjon**
- **Støtte for fremtidig frontend + adminpanel**
