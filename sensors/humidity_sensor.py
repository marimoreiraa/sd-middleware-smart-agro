from sensors.sensor_base import SensorBase
import random

class HumiditySensor(SensorBase):
    def __init__(self, topic="agriculture/sensors/humidity"):
        super().__init__("Sensor de Umidade", topic, "%")

    def generate_value(self):
        return round(random.uniform(30.0, 90.0), 2)
