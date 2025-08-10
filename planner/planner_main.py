# -*- coding: utf-8 -*-
"""
智能灯光控制主程序（增量式）
每 10 秒读取一次当前光照值 (lux)，如果太暗就一次只开一盏灯；
如果太亮就一次只关一盏灯。每次动作后等待传感器缓冲，再继续判断。

依赖:
- pyperplan  (pip install pyperplan)
- paho-mqtt  (pip install paho-mqtt)
- influx_utils.get_current_luminance 
- domain.pddl                        
"""
from __future__ import annotations

import json
import logging
import re
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import paho.mqtt.client as mqtt
from influx_utils import get_current_luminance  # 每 10 秒返回一次 lux 浮点值

# ================== 参数区 ==================
LOW_THRESHOLD = 100      # lux < 100  → 太暗，需要增加亮度（一次开一盏）
HIGH_THRESHOLD = 300     # lux > 300  → 太亮，需要降低亮度（一次关一盏）
CHECK_INTERVAL = 10      # 正常巡检间隔（秒）
SENSOR_SETTLE_SECONDS = 30  # 执行动作后等待传感器“缓冲/更新”的时间（秒）

# ================ MQTT 参数 ================
TOPIC_MAP: Dict[str, str] = {
    "l1": "plugwise/control/plus",     # 每盏灯一个子 topic
    "l2": "plugwise/control/circle",
}
DEFAULT_TOPIC = "plugwise/control/circle"  # 若没配到，就用默认
MQTT_HOST = "mosquitto"
MQTT_PORT = 1883
MQTT_QOS = 1
MQTT_RETAIN = False
MQTT_KEEPALIVE = 60
MQTT_USERNAME: Optional[str] = None
MQTT_PASSWORD: Optional[str] = None

# ================ 正则与路径 ================
STEP_RE = re.compile(r"\(\s*([^\s()]+)\s+([^\s()]+)\s*\)", re.I)  # 捕获: (ACTION LAMP)
BASE_DIR = Path(__file__).resolve().parent
PROBLEM_FILE = BASE_DIR / "problem.pddl"
SOLN_FILE = PROBLEM_FILE.with_suffix(PROBLEM_FILE.suffix + ".soln")  # problem.pddl → problem.pddl.soln
DOMAIN_FILE = BASE_DIR / "domain.pddl"
STATE_FILE = BASE_DIR / "lamp_state.json"

# =============== 工具函数：灯状态持久化 ================

def load_states(lamps: List[str]) -> Dict[str, bool]:
    """读取本地灯状态（若无文件则默认关）。"""
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            # 只保留当前 lamps 列表里存在的键
            return {l: bool(data.get(l, False)) for l in lamps}
        except Exception:
            logging.warning("lamp_state.json 解析失败，按默认关处理。")
    return {l: False for l in lamps}

def save_states(states: Dict[str, bool]) -> None:
    try:
        STATE_FILE.write_text(json.dumps(states, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        logging.error("保存灯状态失败：%s", e)

# =============== 规划问题生成（一次只操作一盏） ================

def decide_goal(lux: float, states: Dict[str, bool], lamps: List[str]) -> Optional[Tuple[str, str]]:
    """
    根据 lux 与当前灯状态，决定本轮目标动作（一次只动一盏）。
    返回 (action, lamp) 如 ("turn-on", "l1") 或 ("turn-off", "l2")。无动作则返回 None。
    """
    if lux < LOW_THRESHOLD:
        # 需要更亮：找第一盏关闭的灯来开
        for l in lamps:
            if not states.get(l, False):
                return ("turn-on", l)
        return None  # 都已开，无能为力，等下一轮
    elif lux > HIGH_THRESHOLD:
        # 需要更暗：找第一盏开启的灯来关（也可反向优先，这里沿用同顺序）
        for l in lamps:
            if states.get(l, False):
                return ("turn-off", l)
        return None  # 都已关，无能为力，等下一轮
    else:
        # 在 [LOW_THRESHOLD, HIGH_THRESHOLD] 之间，保持不动
        return None

def build_problem_for_action(
    action: str, lamp: str, states: Dict[str, bool], lamps: List[str]
) -> None:
    """
    写出只为一个动作设计的 PDDL 问题。初始状态使用真实的灯状态；
    亮/暗标识使用动作需要的全局 flag（turn-on 需要 dark，turn-off 需要 bright）。
    目标只要求该灯达到目标状态。
    """
    if action == "turn-on":
        flag = "(dark)"
        goal = f"(lamp-on {lamp})"
    elif action == "turn-off":
        flag = "(bright)"
        goal = f"(lamp-off {lamp})"
    else:
        raise ValueError(f"未知动作: {action}")

    init_states = [f"(lamp-on {l})" if states.get(l, False) else f"(lamp-off {l})" for l in lamps]
    PROBLEM_FILE.write_text(
        f"""(define (problem light-problem)
  (:domain light-control)
  (:objects {' '.join(lamps)})
  (:init {flag} {' '.join(init_states)})
  (:goal (and {goal}))
)""",
        encoding="utf-8",
    )

# =============== 调用 Planner ===============

def run_planner() -> List[Tuple[str, str]]:
    """调用 pyperplan BFS，返回 (action, lamp) 对列表（小写）。"""
    cmd = ["python3", "-m", "pyperplan", "-s", "bfs", str(DOMAIN_FILE), str(PROBLEM_FILE)]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logging.error("Planner failed (exit %d):\n%s", e.returncode, e.output)
        return []
    logging.debug(out)

    pairs: List[Tuple[str, str]] = []

    # 1) 优先解析 .soln 文件
    if SOLN_FILE.exists():
        for line in SOLN_FILE.read_text(encoding="utf-8").splitlines():
            if m := STEP_RE.search(line):
                pairs.append((m.group(1).lower(), m.group(2).lower()))

    # 2) 备用：从 stdout 解析
    if not pairs:
        for line in out.splitlines():
            if m := STEP_RE.search(line):
                pairs.append((m.group(1).lower(), m.group(2).lower()))

    return pairs

# ================ MQTT 封装 =================

def build_mqtt_client() -> mqtt.Client:
    client = mqtt.Client(client_id="light-planner-controller")
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, password=MQTT_PASSWORD)

    def _on_connect(c, u, f, rc):
        if rc == 0:
            logging.info("已连接 MQTT broker %s:%d", MQTT_HOST, MQTT_PORT)
        else:
            logging.error("MQTT 连接失败，错误码: %s", rc)

    def _on_disconnect(c, u, rc):
        if rc != 0:
            logging.warning("MQTT 非正常断开（rc=%s），将由客户端自动重连。", rc)

    client.on_connect = _on_connect
    client.on_disconnect = _on_disconnect

    client.connect(MQTT_HOST, MQTT_PORT, keepalive=MQTT_KEEPALIVE)
    client.loop_start()
    return client

def publish_action(client: mqtt.Client, lamp: str, action: str) -> None:
    topic = TOPIC_MAP.get(lamp, DEFAULT_TOPIC)
    payload = json.dumps({"action": "on" if action == "turn-on" else "off"}, ensure_ascii=False)
    info = client.publish(topic, payload=payload, qos=MQTT_QOS, retain=MQTT_RETAIN)
    info.wait_for_publish(timeout=5)
    if info.is_published():
        logging.info("已发布到 %s（%s）: %s", topic, lamp, payload)
    else:
        logging.warning("发布未确认：%s -> %s", topic, payload)

# ================ 执行动作并更新本地状态 =================

def act(pairs: List[Tuple[str, str]], mqtt_client: mqtt.Client, states: Dict[str, bool]) -> bool:
    """
    执行动作（通常是一个动作），并更新本地灯状态。
    返回是否执行了至少一个动作。
    """
    if not pairs:
        logging.info(">>> Planner 给出零动作，无需操作")
        return False

    executed = False
    for action, lamp in pairs:
        if action == "turn-on":
            logging.info(">>> 开灯: %s", lamp)
            publish_action(mqtt_client, lamp, "turn-on")
            states[lamp] = True
            executed = True
        elif action == "turn-off":
            logging.info(">>> 关灯: %s", lamp)
            publish_action(mqtt_client, lamp, "turn-off")
            states[lamp] = False
            executed = True
        else:
            logging.warning("未知动作: %s %s", action, lamp)

    if executed:
        save_states(states)
    return executed

# =================== main loop ==================

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

    lamps = list(TOPIC_MAP.keys())  # 按 TOPIC_MAP 顺序决定优先级
    if not DOMAIN_FILE.exists():
        raise FileNotFoundError(f"未找到 {DOMAIN_FILE}, 请将 domain.pddl 放在同目录。")

    states = load_states(lamps)
    logging.info("初始灯状态: %s", states)

    mqtt_client = build_mqtt_client()

    try:
        while True:
            lux = float(get_current_luminance())
            logging.info("当前光照: %.2f lux | 状态: %s", lux, states)

            decision = decide_goal(lux, states, lamps)
            if decision is None:
                logging.info("光照处于 [%d, %d] lux 范围或无可操作灯，跳过动作。",
                             LOW_THRESHOLD, HIGH_THRESHOLD)
                time.sleep(CHECK_INTERVAL)
                continue

            action, lamp = decision
            build_problem_for_action(action, lamp, states, lamps)
            plan = run_planner()
            executed = act(plan, mqtt_client, states)

            # 若执行了动作，则等待传感器缓冲时间，再继续下一轮；
            # 否则按正常巡检间隔。
            if executed:
                logging.info("动作已执行，等待传感器缓冲 %d 秒再评估。", SENSOR_SETTLE_SECONDS)
                time.sleep(SENSOR_SETTLE_SECONDS)
            else:
                time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n已手动终止智能灯光控制程序。")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        logging.info("已断开 MQTT 连接。")

if __name__ == "__main__":
    main()
