from sensors.sensor_manager import SensorManager

sm = SensorManager()
readings = sm.read_all()
print(readings)
