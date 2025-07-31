#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plugwise MQTT controller
- Listens on two topics:
    plugwise/control/plus
    plugwise/control/circle
- Payload must be JSON: {"action": "on"} or {"action": "off"}
"""

from plugwise.api import Stick, Circle
from datetime import datetime
import paho.mqtt.client as mqtt
import json, traceback, os, threading
from time import sleep
import os

# ──────────────────────────  CONFIG  ──────────────────────────
DEFAULT_PORT        = os.getenv("DEFAULT_PORT_PLUGWISE")
PLUS_MAC            = "000D6F0005692B55"
CIRCLE_MAC          = "000D6F0004B1E6C4"

MQTT_BROKER         = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT           = 1883
MQTT_ID             = "plugwise_controller"

TOPIC_PLUS          = "plugwise/control/plus"
TOPIC_CIRCLE        = "plugwise/control/circle"
TOPIC_PLUS_ENERGY   = "plugwise/status/plus"
TOPIC_CIRCLE_ENERGY = "plugwise/status/circle"
# ───────────────────────────────────────────────────────────────

# Init Plugwise stick & devices
stick        = Stick(DEFAULT_PORT)
circle_plus  = Circle(PLUS_MAC, stick)
# circle       = Circle(CIRCLE_MAC, stick)

now = datetime.now()
circle_plus.set_clock(now)
# circle.set_clock(now)

# ───────────────────────  Report Energy ─────────────────────────────
def publish_energy(device: Circle, topic: str, name: str):
    try:
        state = device.get_info()
        power_w = 0.0
        if state["relay_state"] == 1:
            power_w = device.get_power_usage()
        else:
            power_w = 0.0
        payload = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "power": round(power_w, 2)           
        }
        print(payload)
        client.publish(topic, json.dumps(payload), qos=0)
        
        
    except Exception as e:
        print(f"Read {name} energy fail: {e}")

def energy_report_loop():
    while True:
        publish_energy(circle_plus,  TOPIC_PLUS_ENERGY,   "Circle+")
        # publish_energy(circle,       TOPIC_CIRCLE_ENERGY, "Circle")
        sleep(10)

threading.Thread(target=energy_report_loop, daemon=True).start()

# ───────────────────────  Read Day Energy use  ─────────────────────────────
def read_day_energy(device: Circle):
    info = device.get_info()
    current_idx = info['last_logaddr']      
    total_wh = 0.0

    # 24 小时 = 6 个 log buffer（4 h × 6 = 24 h）
    for i in range(6):
        idx = (current_idx - i) % 168          
        for dt, wh in device.get_power_usage_history(idx):
            if dt is not None:                  
                total_wh += wh

    return total_wh / 1000                    
# ───────────────────────  Helper  ─────────────────────────────
def handle_switch(device: Circle, turn_on: bool, name: str):
    """Switch device on/off if state differs."""
    state = device.get_info()
    relay = state["relay_state"]  # 1=on, 0=off
    desired = 1 if turn_on else 0

    if relay == desired:
        print(f"[{name}] already {'ON' if turn_on else 'OFF'}")
        return

    print(f"[{name}] switching {'ON' if turn_on else 'OFF'} …")
    if turn_on:
        device.switch_on()
    else:
        device.switch_off()

# ───────────────────────  MQTT callbacks  ─────────────────────
def on_connect(client, *_):
    print("Connected to MQTT broker")
    client.subscribe([(TOPIC_PLUS, 0), (TOPIC_CIRCLE, 0)])
    print(f"Subscribed to {TOPIC_PLUS} & {TOPIC_CIRCLE}")

def on_message(client, _userdata, msg):
    try:
        data    = json.loads(msg.payload.decode())
        action  = data.get("action")
        topic   = msg.topic

        if topic == TOPIC_PLUS:
            device, name = circle_plus, "Circle+"
        elif topic == TOPIC_CIRCLE:
            device, name = circle, "Circle"
        else:
            print(f"Unknown topic {topic}")
            return

        if action == "on":
            handle_switch(device, True, name)
        elif action == "off":
            handle_switch(device, False, name)
        else:
            print(f"Unknown action '{action}' on {topic}")

    except Exception as e:
        print(f"Error processing message on {msg.topic}: {e}")
        traceback.print_exc()

# ─────────────────────────  MQTT init  ────────────────────────
client = mqtt.Client(client_id=MQTT_ID, clean_session=True)
client.on_connect  = on_connect
client.on_message  = on_message

client.reconnect_delay_set(min_delay=1, max_delay=120)

client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
print("waiting for MQTT messages")
client.loop_forever()
