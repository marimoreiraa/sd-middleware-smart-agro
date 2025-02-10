from datetime import datetime
import os
import sys
from flask import Flask, render_template, request, redirect, url_for
import rpyc

app = Flask(__name__)

# Conectando ao servidor rpyc
client = rpyc.connect("localhost", 18812)

@app.route("/")
def index():
    try:
        controllers_data = client.root.exposed_get_controllers_and_replicas()

        return render_template("index.html", controllers=controllers_data)
    except Exception as e:
        print(f"Erro ao buscar informações dos controladores: {e}")
        return "Erro ao carregar informações dos controladores."


@app.route("/controller/<controller_id>")
def controller_data(controller_id):
    """Retorna os dados dos sensores, atuadores e histórico do controlador selecionado."""
    try:
        # Buscar os dados dos sensores e atuadores
        sensors_data = client.root.exposed_get_sensor_data()
        actuators_status = client.root.exposed_get_actuator_data()

        # Filtrar os dados pelo controlador selecionado
        filtered_sensors = {}
        filtered_actuators = {}

        if controller_id == "lighting":
            filtered_sensors["luminosity"] = sensors_data["luminosity"]
            filtered_actuators["lighting"] = actuators_status["lighting"]
        elif controller_id == "irrigation":
            filtered_sensors["soil_moisture"] = sensors_data["soil_moisture"]
            filtered_actuators["irrigation"] = actuators_status["irrigation"]
        elif controller_id == "cooling":
            filtered_sensors["temperature"] = sensors_data["temperature"]
            filtered_actuators["cooling"] = actuators_status["cooling"]

        # Buscar histórico de dados no MongoDB
        historical_data = client.root.exposed_get_historical_sensor_data(controller_id)

        return render_template("controllers.html", 
                               sensors=filtered_sensors, 
                               actuators=filtered_actuators,
                               selected_controller=controller_id,
                               historical_data=historical_data)
    except Exception as e:
        print(f"Erro ao buscar dados do controlador {controller_id}: {e}")
        return f"Erro ao carregar os dados do controller {controller_id}"



@app.route("/<controller_id>/control_actuators", methods=["GET", "POST"])
def control_actuators(controller_id):
    """Controlar os atuadores manualmente."""
    if request.method == "POST":
        action = request.form["action"]
        client.root.exposed_control_actuators(controller_id, action)
        return redirect(url_for("controller_data", controller_id=controller_id))

    return render_template("toggle_actuators.html",
                           selected_controller=controller_id)

@app.route("/<controller_id>/control_sensors", methods=["GET", "POST"])
def control_sensors(controller_id):
    """Controlar os sensores manualmente."""
    if controller_id == "irrigation":
        sensor_type = "soil-moisture"
    elif controller_id == "cooling":
        sensor_type = "temperature"
    elif controller_id == "lighting":
        sensor_type = "luminosity"
    if request.method == "POST":
        action = request.form["action"]
        client.root.exposed_control_sensors(sensor_type, action)
        return redirect(url_for("controller_data", controller_id=controller_id))
    
    return render_template("toggle_sensors.html",
                           selected_controller=controller_id,
                           selected_sensor=sensor_type)

@app.route("/<controller_id>/simulate_failover", methods=["POST"])
def simulate_failover(controller_id):
    """Simula a falha do controlador selecionado."""
    try:
        print(f"Simulando falha no controlador {controller_id}.")
        client.root.exposed_simulate_failover(controller_id)

        return redirect(url_for('controller_data', controller_id=controller_id))
    except Exception as e:
        print(f"Erro ao simular failover no controlador {controller_id}: {e}")
        return f"Erro ao simular failover para o controlador {controller_id}"

current_port = int(os.environ.get('PORT', 5001))  # Porta padrão 5001 se não especificada

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=current_port)