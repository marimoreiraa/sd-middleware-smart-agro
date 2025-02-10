from sensors.sensor_base import SensorBase
import random

class SoilMoistureSensor(SensorBase):
    def __init__(self, topic="agriculture/sensors/soil_moisture"):
        super().__init__("Sensor de Umidade do Solo", topic, "%")

    def generate_value(self):
        # Simula valores de umidade do solo entre 10% e 60%
        return round(random.uniform(10.0, 60.0), 2)
