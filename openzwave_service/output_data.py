import openzwave
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import logging
import time
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import os

# setting device_name and OpenZWave path( in docker)
device_name = "/dev/ttyACM0"
config_path = "/app/config"  # in docker

# Init Z-Wave
options = ZWaveOption(device_name, config_path=config_path, user_path=".")
options.set_console_output(False)
options.lock()


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s:%(name)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# MQTT client init
mqtt_client = mqtt.Client()
mqtt_broker = os.getenv("MQTT_BROKER", "mosquitto")
mqtt_port = 1883
mqtt_topic = "zwave/sensor_data"

try:
    mqtt_client.connect(mqtt_broker, mqtt_port)
except Exception as e:
    logging.error(f"cannot connect MQTT broker: {e}")
    exit(1)

# init Z-wave
logging.info("Starting Z-Wave network...")
network = ZWaveNetwork(options)
network.start()

# Waiting Z-Wave network
while network.state != network.STATE_READY:
    time.sleep(1)
    logging.info("Network not ready...")

logging.info("Network is ready!")

# Z-wave nodes
logging.info("========= Node List =========")
for node_id in network.nodes:
    node = network.nodes[node_id]
    logging.info(f"Node {node_id}: {node.product_name} - {node.manufacturer_name}")

# set param
logging.info("========= Setup Param =========")
for node_id in network.nodes:
    try:
        network.nodes[node_id].set_config_param(111, 10)
    except Exception as e:
        logging.warning(f"Node {node_id}: Failed to set param 111 - {e}")
time.sleep(0.5)

# sensor_labels = [
#     "Air Temperature", "Temperature",
#     "Illuminance", "Luminance",
#     "Humidity", "Relative Humidity",
#     "Ultraviolet", "UV",
#     "Voltage", "Current", "Power", "Energy"
# ]

# main loop
logging.info("========= Start Main Loop =========")
while True:
    payload = {
        "time": datetime.now().isoformat()
    }

    for node_id, node in network.nodes.items():
        if not node.is_ready:
            continue  # skip the useless node

        for val_id in node.get_sensors():
            val_obj = node.values[val_id]
            label = val_obj.label
            data = val_obj.data

            if label in ["Luminance"]:
                if isinstance(data, (int, float)):
                    payload[label] = data 

    message = json.dumps(payload)
    mqtt_client.publish(mqtt_topic, message)
    logging.info(f" MQTT Data: {message}")

    time.sleep(10)