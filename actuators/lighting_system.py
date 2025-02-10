from actuators.actuator_base import ActuatorBase

class LightingActuator(ActuatorBase):
    def __init__(self, topic="agriculture/actuators/lighting"):
        super().__init__("Iluminação", topic)

    def perform_action(self):
        if self.active:
            print("💡 Sistema de iluminação ativado! Garantindo luz para as plantas.")
