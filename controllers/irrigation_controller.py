from controllers.controller_base import ControllerBase
from sensors.soil_moisture_sensor import SoilMoistureSensor
from actuators.irrigation_system import IrrigationActuator

class IrrigationController(ControllerBase):
    def __init__(self,role="Primary"):
        super().__init__(
            name="Irrigação",
            sensor_topic="agriculture/sensors/soil_moisture",
            actuator_topic="agriculture/actuators/irrigation",
            limits={"min_moisture": 30},
            role=role
        )
        self.sensor = SoilMoistureSensor()
        self.actuator = IrrigationActuator()

    def process_sensor_data(self, value):
        if value < self.limits["min_moisture"]:
            print(f"{self.name}: Umidade baixa ({value}%), ativando irrigação.")
            self.send_command("ON")
        else:
            print(f"{self.name}: Umidade adequada ({value}%), desativando irrigação.")
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

