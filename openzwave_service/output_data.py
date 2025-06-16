# output_data.py

import openzwave
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import logging
import time

# 配置串口和OpenZWave路径
device_name = "/dev/ttyACM0"
#config_path = "/home/wenhaocao/desktop/Intelligent-Lighting-system/openzwave_service/open-zwave/config"     #in local
config_path = "/app/config"  # in docker

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

# 定义传感器 label 列表（可以根据需要补充）
sensor_labels = [
    "Air Temperature",
    "Temperature",
    "Illuminance",
    "Luminance",
    "Humidity",
    "Relative Humidity",
    "Ultraviolet",
    "UV",
    "Voltage",
    "Current",
    "Power",
    "Energy"
]

# 主循环
logging.info("========= Start Main Loop =========")
while True:
    for node_id in network.nodes:
        node = network.nodes[node_id]
        print(f"\n--- Node {node_id}: {node.product_name} ---")
        # 打印所有 value
        for val_id, val_obj in node.values.items():
            print(f"{val_obj.label}: {val_obj.data}")
        # 打印 sensor value
        print("--- Sensors ---")
        for val_id in node.get_sensors():
            val_obj = node.values[val_id]
            if val_obj.label in sensor_labels:
                print(f"{val_obj.label}: {val_obj.data}")
    print("\n======================\n")
    time.sleep(10)  # 等待 30 秒继续轮询
