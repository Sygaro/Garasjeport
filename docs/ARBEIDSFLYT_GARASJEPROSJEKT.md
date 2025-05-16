# 🚀 Arbeidsflyt for Garasjeprosjektet – Git og utvikling

## 📁 Grenestruktur

- **main**: Produksjonsklar og stabil kode
- **dev**: Samler ferdigtestede moduler før de slås sammen til `main`
- **feature/<modulnavn>**: Midlertidige grener for hver ny funksjonalitet

---

## 🔄 Typisk utviklingssyklus

1. **Start ny funksjon/modul:**
   ```bash
   ./ny_feature.sh kalibrering
   ```

2. **Utvikle, test, commit:**
   ```bash
   git add .
   git commit -m "Startet kalibreringsmodul"
   ```

3. **Push til GitHub:**
   ```bash
   git push
   ```

4. **Når klar, lag Pull Request fra:**
   - `feature/kalibrering` ➝ `dev`

5. **Når `dev` er testet:**
   - Lag PR fra `dev` ➝ `main`
   - Tag ny release: `git tag -a v0.3.0 -m "Kalibrering fullført"`

---

## 📦 Tips

- Bruk `README_DEV.md` til å logge fremdrift
- Tag hver ferdig modul
- Ikke jobb direkte i `main` eller `dev`
- Bruk backup-scriptet jevnlig

---

🛠️ Sist oppdatert: 2025-05-05
