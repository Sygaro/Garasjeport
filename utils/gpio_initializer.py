import pigpio

def configure_gpio_pins(sensor_pins, pull, pi=None):
    if pi is None:
        pi = pigpio.pi()

    pull_mode = {
        "up": pigpio.PUD_UP,
        "down": pigpio.PUD_DOWN,
        "off": pigpio.PUD_OFF
    }.get(pull.lower(), pigpio.PUD_OFF)

    for port, sensors in sensor_pins.items():
        for sensor_type, gpio in sensors.items():
            pi.set_mode(gpio, pigpio.INPUT)
            pi.set_pull_up_down(gpio, pull_mode)
