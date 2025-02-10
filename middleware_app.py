from datetime import datetime
import pymongo
import rpyc
from rpyc import ThreadPoolServer
from controllers.irrigation_controller import IrrigationController
from controllers.lighting_controller import LightingController
from controllers.cooling_controller import CoolingController

class Middleware:
    VALIDATION_LIMITS = {
        "soil_moisture": (10, 60),  # Intervalo esperado para umidade do solo
        "luminosity": (100, 10000),   # Intervalo esperado para luminosidade
        "temperature": (15, 35)    # Intervalo esperado para temperatura
    }

    def __init__(self):
        # Inicializando os controladores e as réplicas
        self.irrigation_controllers = []
        self.cooling_controllers = []
        self.lighting_controllers = []

        # Criando 1 primario e 2 réplicas para cada controlador
        self.create_replicas(IrrigationController, self.irrigation_controllers, 3)
        self.create_replicas(CoolingController, self.cooling_controllers, 3)
        self.create_replicas(LightingController, self.lighting_controllers, 3)

        # Inicia todos os controladores
        self.start_all_controllers()

    def validate_sensor_data(self, sensor_type, value):
        """Valida os dados do sensor para verificar se estão dentro dos limites aceitáveis."""
        if sensor_type in self.VALIDATION_LIMITS:
            min_val, max_val = self.VALIDATION_LIMITS[sensor_type]
            if min_val <= value <= max_val:
                return True
            print(f"[VALIDAÇÃO] {sensor_type} com valor inválido: {value}")
        return False

    def create_replicas(self, controller_class, controller_list, num_replicas):
        """Cria as réplicas dos controladores e as adiciona à lista."""
        for i in range(num_replicas):
            role = "Primary" if i == 0 else f"Replica{i}"
            controller_instance = controller_class(role=role)  # Passe o papel para o controlador
            controller_list.append(controller_instance)
            print(f"{controller_instance.name} criado e adicionado à lista.")

    
    def get_controllers_and_replicas(self):
        """Retorna uma lista de controladores e suas réplicas."""
        controllers_info = {
            "irrigation": [{"name": ctrl.name, "role": ctrl.role} for ctrl in self.irrigation_controllers],
            "cooling": [{"name": ctrl.name, "role": ctrl.role} for ctrl in self.cooling_controllers],
            "lighting": [{"name": ctrl.name, "role": ctrl.role} for ctrl in self.lighting_controllers]
        }
        return controllers_info
    
    def start_all_controllers(self):
        """Inicia os controladores principais (e sensores/atuadores)."""
        print("Iniciando todos os controladores...")
        self.irrigation_controllers[0].start()
        self.cooling_controllers[0].start()
        self.lighting_controllers[0].start()

        # Liga sensores/atuadores
        self.irrigation_controllers[0].control_sensor("on")
        self.irrigation_controllers[0].control_actuator("on")
        self.cooling_controllers[0].control_sensor("on")
        self.cooling_controllers[0].control_actuator("on")
        self.lighting_controllers[0].control_sensor("on")
        self.lighting_controllers[0].control_actuator("on")

    def activate_next_controller(self, controllers):
        """Promove a próxima réplica como o controlador principal."""
        if len(controllers) > 1:
            controllers[0].stop()
            failed_controller = controllers.pop(0)  # Remove o controlador principal falho
            new_primary = controllers[0]  # Próximo na lista se torna o principal
            print(f"[FAILOVER] {failed_controller.name} falhou. Promovendo {new_primary.name} como novo principal.")
            new_primary.recover_state_from_db()
            new_primary.start()  # Inicia o controlador
            new_primary.control_sensor("on")  # Liga o sensor
            new_primary.control_actuator("on")  # Liga o atuador
            self.add_new_replica(type(new_primary), controllers)
        else:
            print("[ERRO] Não há réplicas disponíveis para ativar.")

    def add_new_replica(self, controller_class, controllers):
        """Adiciona uma nova réplica à lista de controladores."""
        controller_instance = controller_class()
        controllers.append(controller_instance)  # Adiciona à lista de réplicas
        print(f"[NOVO CONTROLADOR] Réplica {controller_instance.name} adicionada à lista de controladores.")

    def simulate_failover(self, controllers):
        """Força a troca do controlador principal."""
        print("[SIMULAÇÃO] Simulando falha do controlador principal...")
        self.activate_next_controller(controllers)

    def get_sensor_data(self):
        """Retorna os dados atuais dos sensores após validação."""
        sensor_data = {
            "soil_moisture": self.irrigation_controllers[0].get_sensor_last_value(),
            "luminosity": self.lighting_controllers[0].get_sensor_last_value(),
            "temperature": self.cooling_controllers[0].get_sensor_last_value()
        }

        # Valida os dados dos sensores
        validated_data = {}
        for sensor_type, value in sensor_data.items():
            if self.validate_sensor_data(sensor_type, value):
                validated_data[sensor_type] = value
            else:
                print(f"[ALERTA] Dado inválido ignorado: {sensor_type}={value}")
        
        return validated_data

    def get_actuator_data(self):
        """Retorna os dados atuais dos atuadores."""
        return {
            "irrigation": str(self.irrigation_controllers[0].get_actuator_last_value()),
            "lighting": str(self.lighting_controllers[0].get_actuator_last_value()),
            "cooling": str(self.cooling_controllers[0].get_actuator_last_value())
        }

    def control_actuators(self, actuator_type, action):
        """Encaminha o comando de controle para os atuadores."""
        if actuator_type == "irrigation":
            self.irrigation_controllers[0].control_actuator(action)
        elif actuator_type == "lighting":
            self.lighting_controllers[0].control_actuator(action)
        elif actuator_type == "cooling":
            self.cooling_controllers[0].control_actuator(action)
        else:
            print(f"Ação inválida para o atuador: {actuator_type}")

    def control_sensors(self, sensor_type, action):
        """Encaminha o comando de controle para os sensores."""
        if sensor_type == "soil-moisture":
            self.irrigation_controllers[0].control_sensor(action)
        elif sensor_type == "lighting":
            self.lighting_controllers[0].control_sensor(action)
        elif sensor_type == "temperature":
            self.cooling_controllers[0].control_sensor(action)
        else:
            print(f"Ação inválida para o sensor: {sensor_type}")

    def get_historical_sensor_data(self, controller_name):
        """Retorna os dados históricos do sensor de um controlador específico."""
        if controller_name == "irrigation":
            return self.irrigation_controllers[0].get_historical_sensor_data()
        elif controller_name == "lighting":
            return self.lighting_controllers[0].get_historical_sensor_data()
        elif controller_name == "cooling":
            return self.cooling_controllers[0].get_historical_sensor_data()
        else:
            return []

class MiddlewareService(rpyc.Service):
    def __init__(self, middleware):
        self.middleware = middleware

    def on_connect(self, conn):
        print("Cliente conectado")

    def on_disconnect(self, conn):
        print("Cliente desconectado")

    def exposed_get_sensor_data(self):
        return self.middleware.get_sensor_data()

    def exposed_get_actuator_data(self):
        return self.middleware.get_actuator_data()

    def exposed_control_actuators(self, actuator_type, action):
        self.middleware.control_actuators(actuator_type, action)

    def exposed_control_sensors(self, sensor_type, action):
        self.middleware.control_sensors(sensor_type, action)

    def exposed_simulate_failover(self, controller_type):
        """Simula o failover forçando a troca do controlador principal."""
        if controller_type == "irrigation":
            self.middleware.simulate_failover(self.middleware.irrigation_controllers)
        elif controller_type == "cooling":
            self.middleware.simulate_failover(self.middleware.cooling_controllers)
        elif controller_type == "lighting":
            self.middleware.simulate_failover(self.middleware.lighting_controllers)
        else:
            print("[ERRO] Tipo de controlador inválido para simular failover.")

    def exposed_get_historical_sensor_data(self, controller_name):
        return self.middleware.get_historical_sensor_data(controller_name)
    
    def exposed_get_controllers_and_replicas(self):
        return self.middleware.get_controllers_and_replicas()

def start_service():
    middleware = Middleware()

    # Iniciar servidor RPyC
    service = MiddlewareService(middleware)
    server = ThreadPoolServer(service, port=18812)
    print("Servidor RPyC rodando em localhost:18812")
    server.start()

if __name__ == "__main__":
    start_service()
