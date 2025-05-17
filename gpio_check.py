# gpio_check.py
import lgpio

chip = lgpio.gpiochip_open(0)
print("GPIO chip 0 opened OK.")
lgpio.gpiochip_close(chip)
