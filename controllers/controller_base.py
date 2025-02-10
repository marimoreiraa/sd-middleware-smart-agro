import paho.mqtt.client as mqtt
import json
import pymongo
from datetime import datetime
import time

class ControllerBase:
    def __init__(self, name, sensor_topic, actuator_topic, limits, role="Primary", db_name="agriculture_db", collection_name="controller_data"):
        self.name = f"{name} ({role})"  # Nome dinâmico com o papel
        self.role = role  # Papel do controlador
        self.sensor_topic = sensor_topic
        self.sensor_last_value = None
        self.actuator_topic = actuator_topic
        self.actuator_last_value = None
        self.limits = limits
        self.client = mqtt.Client(f"Controller_{self.name}")

        # Configuração do MongoDB
        self.mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.mongo_client[db_name]
        self.collection = self.db[collection_name]

        # Variável para armazenar o tempo da última mensagem recebida
        self.last_message_time = None

    def connect(self, broker="localhost", port=1883):
        self.client.connect(broker, port)
        self.client.on_message = self.on_message
        self.client.subscribe(self.sensor_topic)
        print(f"{self.name} conectado e monitorando {self.sensor_topic}")

    def on_message(self, client, userdata, message):
        try:
            data = json.loads(message.payload.decode())
            value = data["valor"]
            print(f"{self.name} - Valor recebido do sensor: {value}")
            self.process_sensor_data(value)
            self.sensor_last_value = value

            # Atualiza a hora da última mensagem recebida
            self.last_message_time = datetime.utcnow()

            # Armazenar dados do sensor no MongoDB
            self.store_data_in_db(data_type="sensor", value=value)

        except (json.JSONDecodeError, KeyError):
            print(f"{self.name}: Mensagem inválida recebida.")

    def process_sensor_data(self, value):
        raise NotImplementedError("Este método deve ser implementado na classe derivada.")

    def send_command(self, command):
        self.actuator_last_value = command
        self.client.publish(self.actuator_topic, command)
        print(f"{self.name}: Comando enviado para {self.actuator_topic} - {command}")

        # Armazenar estado do atuador no MongoDB
        self.store_data_in_db(data_type="actuator", value=command)

    def store_data_in_db(self, data_type, value):
        """Armazena os dados no MongoDB."""
        document = {
            "controller": self.name,
            "timestamp": datetime.utcnow(),
            "data_type": data_type,
            "topic": self.sensor_topic if data_type == "sensor" else self.actuator_topic,
            "value": value
        }
        self.collection.insert_one(document)
        print(f"{self.name}: Dados armazenados no MongoDB: {document}")

    def recover_state_from_db(self):
        """Recupera o estado mais recente do MongoDB e o aplica ao controlador."""
        try:
            # Recupera os dados do sensor mais recente
            last_sensor_data = self.collection.find_one(
                {"controller": self.name, "data_type": "sensor"},
                sort=[("timestamp", pymongo.DESCENDING)]
            )

            # Recupera o estado mais recente do atuador
            last_actuator_data = self.collection.find_one(
                {"controller": self.name, "data_type": "actuator"},
                sort=[("timestamp", pymongo.DESCENDING)]
            )

            # Atualiza os atributos do controlador
            if last_sensor_data:
                self.sensor_last_value = last_sensor_data["value"]
                print(f"{self.name}: Estado do sensor recuperado: {self.sensor_last_value}")

            if last_actuator_data:
                self.actuator_last_value = last_actuator_data["value"]
                print(f"{self.name}: Estado do atuador recuperado: {self.actuator_last_value}")

        except Exception as e:
            print(f"{self.name}: Erro ao recuperar estado do MongoDB: {e}")

    def start(self):
        self.connect()
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
        print(f"{self.name} desconectado do broker MQTT")

    def get_sensor_last_value(self):
        return self.sensor_last_value
    
    def get_actuator_last_value(self):
        return self.actuator_last_value
    
    def control_sensor(self, action):
        raise NotImplementedError("Este método deve ser implementado na classe derivada.")

    def control_actuator(self, action):
        raise NotImplementedError("Este método deve ser implementado na classe derivada.")

    def get_historical_sensor_data(self, limit=50):
        """Busca os dados históricos do sensor no MongoDB."""
        try:
            # Recupera os dados mais recentes para o sensor
            historical_data = self.collection.find(
                {"controller": self.name, "data_type": "sensor"},
                sort=[("timestamp", pymongo.DESCENDING)]
            ).limit(limit)
            # Formata os dados como uma lista de dicionários
            formatted_data = []
            for d in historical_data:
                # Converte o timestamp para ISO 8601
                iso_timestamp = d["timestamp"].isoformat() if isinstance(d["timestamp"], datetime) else str(d["timestamp"])
                formatted_data.append({"timestamp": iso_timestamp, "value": d["value"]})

            return formatted_data
        except Exception as e:
            print(f"{self.name}: Erro ao buscar dados históricos: {e}")
            return []

