import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def test_callback(channel):
    print(f"Sensor endret: {channel}")

GPIO.add_event_detect(5, GPIO.BOTH, callback=test_callback)
input("Trykk Enter for å avslutte")
GPIO.cleanup()
