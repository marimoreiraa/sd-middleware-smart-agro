import paho.mqtt.client as mqtt
import time
import random
import threading
import json

class SensorBase:
    def __init__(self, sensor_name, topic, unit, broker="localhost", port=1883):
        self.sensor_name = sensor_name
        self.topic = topic
        self.unit = unit
        self.broker = broker
        self.port = port
        self.active = False
        self.interval = 30  # Intervalo padrão de publicação em segundos
        self.client = mqtt.Client(sensor_name)
        self.thread = None

    def connect(self):
        self.client.connect(self.broker, self.port, 60)
        print(f"{self.sensor_name} conectado ao broker MQTT.")

    def disconnect(self):
        self.client.disconnect()
        print(f"{self.sensor_name} desconectado do broker MQTT.")

    def generate_value(self):
        """Deve ser implementado por sensores específicos."""
        raise NotImplementedError("Este método deve ser implementado pela classe filha.")

    def publish_data(self):
        while self.active:
            value = self.generate_value()
            payload = {"valor": value, "unidade": self.unit}
            self.client.publish(self.topic, json.dumps(payload))
            print(f"{self.sensor_name} publicado: {payload}")
            time.sleep(self.interval)

    def start(self):
        if not self.active:
            self.active = True
            self.connect()
            self.thread = threading.Thread(target=self.publish_data)
            self.thread.start()
            print(f"{self.sensor_name} ativado.")

    def stop(self):
        if self.active:
            self.active = False
            if self.thread and self.thread.is_alive():
                self.thread.join()
            self.disconnect()
            print(f"{self.sensor_name} desativado.")
