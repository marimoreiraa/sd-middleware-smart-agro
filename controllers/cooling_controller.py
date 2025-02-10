from controllers.controller_base import ControllerBase
from sensors.temperature_sensor import TemperatureSensor
from actuators.cooling_system import CoolingActuator

class CoolingController(ControllerBase):
    def __init__(self, role="Primary"):
        super().__init__(
            name="Refrigeração",
            sensor_topic="agriculture/sensors/temperature",
            actuator_topic="agriculture/actuators/cooling",
            limits={"max_temperature": 30},
            role=role
        )
        self.sensor = TemperatureSensor()
        self.actuator = CoolingActuator()

    def process_sensor_data(self, value):
        if value > self.limits["max_temperature"]:
            print(f"{self.name}: Temperatura alta ({value}°C), ativando refrigeração.")
            self.send_command("ON")
        else:
            print(f"{self.name}: Temperatura adequada ({value}°C), desativando refrigeração.")
            self.send_command("OFF")

    def control_sensor(self, action):
        """Liga ou desliga o sensor."""
        if action == "on":
            print(f"{self.name}: Sensor ativado.")
            self.sensor.start()
        elif action == "off":
            print(f"{self.name}: Sensor desativado.")
            self.sensor.stop()
        else:
            print(f"{self.name}: Ação inválida para sensor - {action}")
    
    def control_actuator(self, action):
        """Liga ou desliga o atuador."""
        if action == "on":
            self.send_command("ON")
            print(f"{self.name}: Atuador ligado.")
        elif action == "off":
            self.send_command("OFF")
            print(f"{self.name}: Atuador desligado.")
        else:
            print(f"{self.name}: Ação inválida para atuador - {action}")
