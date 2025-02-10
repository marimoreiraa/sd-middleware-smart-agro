from sensors.sensor_base import SensorBase
import random

class TemperatureSensor(SensorBase):
    def __init__(self, topic="agriculture/sensors/temperature"):
        super().__init__("Sensor de Temperatura", topic, "°C")

    def generate_value(self):
        return round(random.uniform(15.0, 35.0), 2)
