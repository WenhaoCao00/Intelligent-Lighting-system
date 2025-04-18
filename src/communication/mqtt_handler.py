import paho.mqtt.client as mqtt
import json
import time
import random

# MQTT 代理配置
broker_address = "localhost"  # MQTT 代理地址
broker_port = 1883           # MQTT 代理端口
topic = "sensors/iot_simulator"  # 发送到的主题

# 创建 MQTT 客户端
client = mqtt.Client()

# 连接到 MQTT 服务器
client.connect(broker_address, broker_port)

while True:
    # 生成新的数据（每次循环都会覆盖旧数据）
    data = {
        "equippment_name": "sensor",
        "timestamp": int(time.time()),
        "Air Temperature": round(random.uniform(20.0, 30.0), 1),  # 随机温度
        "Humidity": round(random.uniform(50.0, 70.0), 1),        # 随机湿度
        "Illuminance": round(random.uniform(200.0, 400.0), 1),   # 随机光照
        "Ultraviolet": round(random.uniform(0.0, 10.0), 1),      # 随机紫外线
    }
    
    # 将数据转换为 JSON 格式
    message = json.dumps(data)
    
    # 发布消息到指定主题
    client.publish(topic, message)
    
    print(f"已发送数据: {message}")
    
    # 等待 10 秒
    time.sleep(10)

# 断开连接（此代码不会执行到这里，除非手动停止程序）
client.disconnect()