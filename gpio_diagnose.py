# Fil: gpio_diagnose.py
# Formål: Tester GPIO sensor-pinner for edge detection, viser statusendringer

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# Sensorpinner hentet fra config.json
sensor_pins = {
    "port1": {"open": 23, "closed": 24},
    "port2": {"open": 20, "closed": 21}
}

def sensor_callback(pin):
    state = GPIO.input(pin)
    print(f"📟 Endring på GPIO {pin}: {'HØY (åpen)' if state else 'LAV (lukket)'}")

# Setup og registrer hendelser
for port, pos_pins in sensor_pins.items():
    for status, pin in pos_pins.items():
        try:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=sensor_callback, bouncetime=200)
            print(f"✔️ Registrert edge detection for GPIO {pin} ({port} - {status})")
        except RuntimeError as e:
            print(f"❌ Klarte ikke registrere GPIO {pin} ({port} - {status}): {e}")

print("\n➡️ Trykk Ctrl+C for å avslutte")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Avslutter og rydder opp")
    GPIO.cleanup()