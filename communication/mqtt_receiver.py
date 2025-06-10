# mqtt_receiver.py

import paho.mqtt.client as mqtt
import json

# MQTT 代理配置
broker_address = "192.168.2.103"    # 如果 Raspberry Pi 自己是 broker，就用 localhost
broker_port = 1883
topic = "sensors/iot_simulator" # 订阅的主题，和 publisher 保持一致

# 定义 MQTT 回调函数 - 连接成功时
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
        client.subscribe(topic)  # 订阅主题
    else:
        print(f"❌ Failed to connect, return code {rc}")

# 定义 MQTT 回调函数 - 接收到消息时
def on_message(client, userdata, msg):
    try:
        # 解码 payload，并尝试将其解析为 JSON
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        
        print(f"\n📥 Received message on topic {msg.topic}:")
        print(json.dumps(data, indent=4))
    except Exception as e:
        print(f"Error parsing message: {e}")

# 创建 MQTT 客户端
client = mqtt.Client()

# 绑定回调函数
client.on_connect = on_connect
client.on_message = on_message

# 连接到 MQTT Broker
client.connect(broker_address, broker_port)

# 启动一个网络循环，等待消息（这个是阻塞式循环）
print("📡 Waiting for messages...")
client.loop_forever()
