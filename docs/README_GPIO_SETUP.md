
# 📦 GPIO Setup – Raspberry Pi (RPi 5 & Zero) – libgpiod 2.x

## ℹ️ Om biblioteket

Prosjektet bruker `libgpiod` – et moderne GPIO-bibliotek for Linux, som erstatter eldre `/sys/class/gpio`-grensesnitt.

- **C-bibliotek:** libgpiod v2.3.x
- **Python bindings:** gpiod 2.3.0

Dette gir rask og responsiv edge-detection **uten polling**, støtter både `BIAS_PULL_UP`, `BOTH_EDGES`, og er kompatibelt med **RPi 5 / Zero**.

---

## 🚫 Hvorfor `pip install gpiod` ikke er nok

- `pip` installerer **kun bindings**, ikke C-biblioteket
- Mange pip-versjoner mangler støtte for:
  - `.chip_path`, `.offset()`, `.event_read()`
  - Dynamisk deteksjon av gpiochipX
- På Raspberry Pi 5 feiler ofte `Chip(...)` med `FileNotFoundError`

---

## ✅ Løsning: Manuell bygging av libgpiod 2.x

```bash
sudo apt install -y git build-essential meson ninja-build python3-dev libtool m4 autoconf
git clone https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git
cd libgpiod
git checkout v2.3.x
meson setup builddir
ninja -C builddir
sudo ninja -C builddir install
sudo ldconfig
```

Python-bindings installeres så via `pip` (etter systembiblioteket er på plass):

```bash
pip install --no-binary=:all: gpiod
```

---

## ✅ Resultat

- Fungerer med både RPi Zero og RPi 5
- Full støtte for GPIO uten sudo (hvis bruker er i `gpio`-gruppen)
- Brukes i `garage_controller.py` for:
  - Rele-pulser (output)
  - Sensor-endringer (input med event-handling)

