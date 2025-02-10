from sensors.sensor_base import SensorBase
import random

class LightSensor(SensorBase):
    def __init__(self, topic="agriculture/sensors/light"):
        super().__init__("Sensor de Luminosidade", topic, "lux")

    def generate_value(self):
        # Simula valores de luminosidade em lux entre 100 e 10000
        return random.randint(100, 10000)
