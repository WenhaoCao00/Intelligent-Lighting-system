"""智能灯光控制主程序

每 10 秒读取一次当前光照值 (lux)，
根据阈值自动规划并执行开/关灯动作。

依赖:
- pyperplan  (pip install pyperplan)
- paho-mqtt  (pip install paho-mqtt)
- influx_utils.get_current_luminance  ← 你自己的实现
- domain.pddl                       ← 与本文件同目录，见配套示例
"""

from __future__ import annotations

import json
import logging
import re
import subprocess
import time
from pathlib import Path
from typing import List, Optional

import paho.mqtt.client as mqtt
from influx_utils import get_current_luminance  # 每 10 秒返回一次 lux 浮点值

# ================== 参数区 ==================
LOW_THRESHOLD = 100     # lux < 100  → 太暗，开灯
HIGH_THRESHOLD = 300    # lux > 300  → 太亮，关灯
CHECK_INTERVAL = 10     # 秒

# ================ MQTT 参数 ================
TOPIC_CIRCLE = "plugwise/control/circle"
MQTT_HOST = "mosquitto"
MQTT_PORT = 1883
MQTT_QOS = 1
MQTT_RETAIN = False
MQTT_KEEPALIVE = 60
MQTT_USERNAME: Optional[str] = None  # 如需认证，填用户名
MQTT_PASSWORD: Optional[str] = None  # 如需认证，填密码

# ================ 正则与路径 ================
STEP_RE = re.compile(r"\(\s*([^) ]+)\s*", re.I)  # 捕获 (ACTION …)
PROBLEM_FILE = Path("problem.pddl")
SOLN_FILE = PROBLEM_FILE.with_suffix(PROBLEM_FILE.suffix + ".soln")  # problem.pddl → problem.pddl.soln
DOMAIN_FILE = Path("domain.pddl")

# =============== PDDL 生成器 ================

def build_problem(lux: float) -> bool:
    """根据当前 lux 写出 problem.pddl。

    返回值:
        True  – 需要规划 (暗或亮)
        False – 亮度在阈值之间，无需动作
    """
    if lux < LOW_THRESHOLD:                # 太暗 ➜ 开灯
        init_parts = ["(dark)", "(lamp-off)"]
        goal = "(lamp-on)"
    elif lux > HIGH_THRESHOLD:             # 太亮 ➜ 关灯
        init_parts = ["(bright)", "(lamp-on)"]
        goal = "(lamp-off)"
    else:
        return False  # 无需动作

    PROBLEM_FILE.write_text(f"""
(define (problem light-problem)
  (:domain light-control)
  (:init {' '.join(init_parts)})
  (:goal {goal})
)
""".strip())
    return True

# =============== 调用 Planner ===============

def run_planner() -> List[str]:
    """调用 pyperplan BFS，返回动作序列（小写）。"""
    cmd = [
        "python3",
        "-m",
        "pyperplan",
        "-s",
        "bfs",
        str(DOMAIN_FILE),
        str(PROBLEM_FILE),
    ]
    # pyperplan 可能打印大量日志；保留 stdout 便于调试
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logging.error("Planner failed (exit %d):\n%s", e.returncode, e.output)
        return []
    logging.debug(out)

    actions: List[str] = []

    # 1) 优先解析 .soln 文件
    if SOLN_FILE.exists():
        for line in SOLN_FILE.read_text().splitlines():
            if m := STEP_RE.search(line):
                actions.append(m.group(1).lower())

    # 2) 备用：stdout 里抓（换别的搜索算法也管用）
    if not actions:
        for line in out.splitlines():
            if m := STEP_RE.search(line):
                actions.append(m.group(1).lower())

    return actions

# ================ MQTT 封装 =================

def build_mqtt_client() -> mqtt.Client:
    client = mqtt.Client(client_id="light-planner-controller", clean_session=True)
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

    # 连接并开启后台网络循环
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=MQTT_KEEPALIVE)
    client.loop_start()
    return client

def publish_action(client: mqtt.Client, action: str) -> None:
    """向 TOPIC_CIRCLE 发送 {"action":"on/off"}"""
    payload = json.dumps({"action": action}, ensure_ascii=False)
    info = client.publish(TOPIC_CIRCLE, payload=payload, qos=MQTT_QOS, retain=MQTT_RETAIN)
    # 等待发布完成（最多 5 秒）；失败会在重连后由客户端重试
    info.wait_for_publish(timeout=5)
    if info.is_published():
        logging.info("已发布到 %s: %s", TOPIC_CIRCLE, payload)
    else:
        logging.warning("发布未确认（可能因网络/断连，稍后将重试）：%s", payload)

# ================ 执行动作 =================

def act(actions: List[str], mqtt_client: mqtt.Client) -> None:
    if "turn-on" in actions:
        logging.info(">>> 执行动作：开灯")
        # ✅ TODO 已完成：发送 MQTT 指令 {"action":"on"}
        publish_action(mqtt_client, "on")

    elif "turn-off" in actions:
        logging.info(">>> 执行动作：关灯")
        # ✅ TODO 已完成：发送 MQTT 指令 {"action":"off"}
        publish_action(mqtt_client, "off")
    else:
        logging.info(">>> Planner 给出零动作，无需操作")

# =================== 主循环 ==================

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    mqtt_client = build_mqtt_client()

    try:
        while True:
            lux = float(get_current_luminance())
            logging.info("当前光照: %.2f lux", lux)

            if build_problem(lux):
                actions = run_planner()
                act(actions, mqtt_client)
            else:
                logging.info("光照处于 [%d, %d] lux 范围，跳过动作。", LOW_THRESHOLD, HIGH_THRESHOLD)

            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\n已手动终止智能灯光控制程序。")
    finally:
        # 结束前清理 MQTT 连接
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        logging.info("已断开 MQTT 连接。")

if __name__ == "__main__":
    main()
