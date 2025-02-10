from actuators.actuator_base import ActuatorBase

class IrrigationActuator(ActuatorBase):
    def __init__(self, topic="agriculture/actuators/irrigation"):
        super().__init__("Irrigação", topic)

    def perform_action(self):
        if self.active:
            print("💧 Sistema de irrigação ativado! Fornecendo água às plantas.")
