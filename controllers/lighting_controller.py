from controllers.controller_base import ControllerBase
from sensors.light_sensor import LightSensor
from actuators.lighting_system import LightingActuator

class LightingController(ControllerBase):
    def __init__(self,role="Primary"):
        super().__init__(
            name="Iluminação",
            sensor_topic="agriculture/sensors/light",
            actuator_topic="agriculture/actuators/lighting",
            limits={"min_luminosity": 200},
            role=role
        )
        self.sensor = LightSensor()
        self.actuator = LightingActuator()

    def process_sensor_data(self, value):
        if value < self.limits["min_luminosity"]:
            print(f"{self.name}: Luminosidade baixa ({value} lux), ativando iluminação.")
            self.send_command("ON")
        else:
            print(f"{self.name}: Luminosidade adequada ({value} lux), desativando iluminação.")
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
    
