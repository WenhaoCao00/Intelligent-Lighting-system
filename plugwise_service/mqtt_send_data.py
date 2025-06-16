# output_data_mqtt.py

import openzwave
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import logging
import time
import json
import paho.mqtt.client as mqtt

# 配置串口和OpenZWave路径
device_name = "/dev/ttyACM0"
config_path = "/home/wenhaocao/desktop/Intelligent-Lighting-system/open-zwave/config"

# 配置 MQTT
MQTT_BROKER = "192.168.0.103"  # 你的 MQTT Broker 地址
MQTT_PORT = 1883
MQTT_TOPIC = "sensors/zwave"   # 可以自定义 topic

# 初始化 Z-Wave 选项
options = ZWaveOption(device_name, config_path=config_path, user_path=".")
options.set_console_output(False)
options.lock()

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s:%(name)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 启动 Z-Wave 网络
logging.info("Starting Z-Wave network...")
network = ZWaveNetwork(options)
network.start()

# 等待网络准备就绪
while network.state != network.STATE_READY:
    time.sleep(1)
    logging.info("Network not ready...")

logging.info("Network is ready!")

# 打印所有 Node 类型
logging.info("========= Node List =========")
for node_id in network.nodes:
    node = network.nodes[node_id]
    logging.info(f"Node {node_id}: {node.product_name} - {node.manufacturer_name}")

# 设置参数（可选）
logging.info("========= Setup Param =========")
for node_id in network.nodes:
    try:
        network.nodes[node_id].set_config_param(111, 10)
    except Exception as e:
        logging.warning(f"Node {node_id}: Failed to set param 111 - {e}")
time.sleep(0.5)

# 初始化 MQTT 客户端
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()

# 需要关注的传感器 label 列表
sensor_labels = [
    "Air Temperature",
    "Temperature",
    "Illuminance",
    "Luminance",
    "Humidity",
    "Relative Humidity",
    "Ultraviolet",
    "UV"
]

# 主循环
logging.info("========= Start Main Loop =========")
while True:
    for node_id in network.nodes:
        node = network.nodes[node_id]
        
        # 只处理有 sensors 的 node
        sensor_data = {}
        for val_id in node.get_sensors():
            val_obj = node.values[val_id]
            if val_obj.label in sensor_labels:
                sensor_data[val_obj.label] = val_obj.data
        
        if not sensor_data:
            continue  # 如果没有传感器值，跳过该 node
        
        # 打印 Node 信息和传感器数据
        print(f"\n--- Node {node_id}: {node.product_name or 'Unknown'} ---")
        for label, data in sensor_data.items():
            print(f"{label}: {data}")
        
        # 发送到 MQTT
        payload = {
            "node_id": node_id,
            "node_name": node.product_name or "Unknown",
            "timestamp": int(time.time()),
            "sensor_data": sensor_data
        }
        mqtt_client.publish(MQTT_TOPIC, json.dumps(payload))
        logging.info(f"Sent to MQTT: {payload}")
    
    print("\n======================\n")
    time.sleep(30)  # 等待 30 秒继续轮询
