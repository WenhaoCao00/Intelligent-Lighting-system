import openzwave
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import logging
import time
import json

# 配置串口和OpenZWave路径
device_name = "/dev/ttyACM0"
config_path = "/home/pi/venv38/lib/python3.8/site-packages/python_openzwave/ozw_config"

# 初始化 Z-Wave 选项
options = ZWaveOption(device_name, config_path=config_path, user_path=".")
options.set_console_output(False)
options.lock()

# 设置日志
logging.basicConfig(level=logging.INFO)

# 启动 Z-Wave 网络
network = ZWaveNetwork(options)
network.start()

# 等待网络准备就绪
while network.state != network.STATE_READY:
    time.sleep(1)
    logging.info("Network not ready...")

logging.info("Network is ready!")

# 设置参数（可选）
logging.info("========= Setup Param =========")
for node in network.nodes:
    network.nodes[node].set_config_param(111, 10)
time.sleep(0.5)

# 主循环：打印每个节点的传感器数据
while True:
    for node in network.nodes:
        print(f"--- Node {node} ---")
        for val in network.nodes[node].get_sensors():
            label = network.nodes[node].values[val].label
            data = network.nodes[node].values[val].data
            if label in ["Air Temperature", "Illuminance", "Humidity", "Ultraviolet"]:
                print(data)
    print("\n----------------------\n")
    time.sleep(10)
