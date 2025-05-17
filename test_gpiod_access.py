
import gpiod

try:
    chip = gpiod.Chip("gpiochip0")
    print("✅ Tilgang til gpiochip0 OK")
    print(f"Chip navn : {chip.name()}")
    print(f"Chip label: {chip.label()}")
    print(f"Antall linjer: {chip.num_lines()}")
    chip.close()
except Exception as e:
    print("❌ FEIL ved åpning av gpiochip0:", e)
