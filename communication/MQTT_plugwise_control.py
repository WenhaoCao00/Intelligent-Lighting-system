from plugwise.api import *
from time import sleep
from datetime import datetime
import paho.mqtt.client as mqtt
import json
import os

# Configuration
DEFAULT_PORT = "/dev/ttyUSB0"
PLUS_MAC = "000D6F0005692B55"  # Circle+ MAC
MAC = "000D6F0004B1E6C4"       # Circle MAC
MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")   # Replace with your MQTT broker address
MQTT_PORT = 1883
MQTT_TOPIC_PLUS = "plugwise/control/plus"  # Topic for Circle+ commands
MQTT_TOPIC_CIRCLE = "plugwise/control/circle"  # Topic for Circle commands
MQTT_CLIENT_ID = "plugwise_controller"

# Initialize Plugwise Stick and devices
stick = Stick(DEFAULT_PORT)
circle_plus = Circle(PLUS_MAC, stick)
circle = Circle(MAC, stick)

# Set clock for both devices
current_time = datetime.now()
circle_plus.set_clock(current_time)
sleep(1)
circle.set_clock(current_time)
sleep(1)

# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC_PLUS)
        client.subscribe(MQTT_TOPIC_CIRCLE)
        print(f"Subscribed to {MQTT_TOPIC_PLUS} and {MQTT_TOPIC_CIRCLE}")
    else:
        print(f"Failed to connect to MQTT broker with code: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        command = json.loads(payload)
        action = command.get("action")
        topic = msg.topic

        # Determine which device to control based on topic
        if topic == MQTT_TOPIC_PLUS:
            device = circle_plus
            device_name = "Circle+"
        elif topic == MQTT_TOPIC_CIRCLE:
            device = circle
            device_name = "Circle"
        else:
            print(f"Unknown topic: {topic}")
            return

        # Get current state
        state = device.get_info()
        print(f"{device_name} ({device.mac}) current state: {state['relay_state']}")

        # Process action
        if action == "on":
            if state["relay_state"] == 0:
                print(f"Turning on {device_name} ({device.mac})...")
                device.switch_on()
            else:
                print(f"{device_name} ({device.mac}) is already on")
        elif action == "off":
            if state["relay_state"] == 1:
                print(f"Turning off {device_name} ({device.mac})...")
                device.switch_off()
            else:
                print(f"{device_name} ({device.mac}) is already off")
        else:
            print(f"Unknown action for {device_name} ({device.mac}): {action}")

    except Exception as e:
        print(f"Error processing MQTT message on {msg.topic}: {e}")

# Initialize MQTT client
mqtt_client = mqtt.Client(client_id=MQTT_CLIENT_ID)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to MQTT broker
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Initial state check and print for both devices
for device, name in [(circle_plus, "Circle+"), (circle, "Circle")]:
    state = device.get_info()
    print(f"{name} ({device.mac}) state: {state}")
    if state["relay_state"] == 1:
        print(f"{name} ({device.mac}) is on")
    else:
        print(f"{name} ({device.mac}) is off")
    sleep(1)

# Start MQTT loop
try:
    mqtt_client.loop_start()
    print(f"Listening for MQTT messages on {MQTT_TOPIC_PLUS} and {MQTT_TOPIC_CIRCLE}...")
    while True:
        sleep(1)  # Keep the script running
except KeyboardInterrupt:
    print("Shutting down...")
    mqtt_client.loop_stop()
    mqtt_client.disconnect()