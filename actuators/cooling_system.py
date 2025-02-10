from actuators.actuator_base import ActuatorBase

class CoolingActuator(ActuatorBase):
    def __init__(self, topic="agriculture/actuators/cooling"):
        super().__init__("Refrigeração", topic)

    def perform_action(self):
        if self.active:
            print("❄️ Sistema de refrigeração ativado! Resfriando a estufa.")
