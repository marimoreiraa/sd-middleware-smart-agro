import paho.mqtt.client as mqtt
import time

class ActuatorBase:
    def __init__(self, name, topic):
        self.name = name
        self.topic = topic
        self.client = mqtt.Client(f"Actuator_{name}")
        self.active = False

    def connect(self, broker="localhost", port=1883):
        self.client.connect(broker, port)
        self.client.on_message = self.on_message
        self.client.subscribe(self.topic)
        print(f"{self.name} conectado ao broker MQTT e assinando o tópico {self.topic}")

    def on_message(self, client, userdata, message):
        """Recebe comandos e processa ações."""
        command = message.payload.decode()
        if command == "ON":
            self.activate()
        elif command == "OFF":
            self.deactivate()
        else:
            print(f"Comando inválido recebido por {self.name}: {command}")
        self.publish_state()

    def publish_state(self):
        """Publica o estado atual do atuador no tópico de estado."""
        state_topic = f"{self.topic}/state"
        state = "ON" if self.active else "OFF"
        self.client.publish(state_topic, state)
        print(f"{self.name}: Estado publicado no tópico {state_topic} - {state}")


    def activate(self):
        if not self.active:
            self.active = True
            print(f"{self.name} ativado!")
            self.perform_action()

    def deactivate(self):
        if self.active:
            self.active = False
            print(f"{self.name} desativado!")

    def perform_action(self):
        raise NotImplementedError("Este método deve ser implementado pela classe derivada.")

    def start(self):
        self.connect()
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
        print(f"{self.name} desconectado do broker MQTT")
