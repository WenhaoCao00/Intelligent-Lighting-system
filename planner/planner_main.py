#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每 10 秒：
  1. 从数据库取当前亮度 (lux_now)
  2. 生成 problem.pddl
  3. 调 fast-downward 规划 -> 得到 TURN-ON / TURN-OFF / 空计划
  4. 仅打印“开灯 / 关灯 / 无动作”，并更新本地灯状态标记
"""

import os, re, subprocess, time
from pathlib import Path
from datetime import datetime

# ---------- ★ 需要你自己实现 / 修改 ★ ----------
from influx_utils import get_current_luminance  # 返回 float lux
# ------------------------------------------------

PLANNER = os.getenv("PLANNER", "/usr/local/bin/fast-downward")
DOMAIN  = "domain.pddl"
PROBLEM = "problem.pddl"

LOW   = 100          # lux，低于→开灯
HIGH  = 300          # lux，高于→关灯
STEP  = 200          # 必须与 domain.pddl 的 increase/decrease 一致

# ----------------- 本地灯状态（仅打印用） -----------------
lamp_state = False   # False=关, True=开

def lamp_is_on() -> bool:
    return lamp_state

def lamp_on():
    global lamp_state
    lamp_state = True
    print(">>> 执行动作：开灯", flush=True)

def lamp_off():
    global lamp_state
    lamp_state = False
    print(">>> 执行动作：关灯", flush=True)
# --------------------------------------------------------

_PROBLEM_TMPL = """
(define (problem lighting-{ts})
  (:domain smart-lighting)
  (:init
    (= (lum) {lux})
    {lamp}
  )
  (:goal (and (>= (lum) {low}) (<= (lum) {high})))
)
""".strip()

def build_problem(lux: int, lamp_on_flag: bool):
    Path(PROBLEM).write_text(
        _PROBLEM_TMPL.format(
            ts   = datetime.utcnow().isoformat(timespec="seconds"),
            lux  = lux,
            lamp = "(lamp-on)" if lamp_on_flag else "",
            low  = LOW,
            high = HIGH,
        )
    )

def decide_and_act():
    lux_now = get_current_luminance()
    lamp_on_flag = lamp_is_on()

    if LOW <= lux_now <= HIGH and lamp_on_flag == (lux_now < HIGH):
        print(f"[{datetime.now():%H:%M:%S}] {lux_now:.1f} lux OK，跳过")
        return

    build_problem(int(lux_now), lamp_on_flag)

    result = subprocess.run(
        [PLANNER, DOMAIN, PROBLEM,
         "--search", "lazy_greedy([ff()], preferred=[ff()])"],
        text=True, capture_output=True
    )

    actions = re.findall(r"^\s*\(([^)]+)\)", result.stdout, re.MULTILINE)
    acts = [a.lower() for a in actions]

    if "turn-on" in acts:
        print(f"[{datetime.now():%H:%M:%S}] {lux_now:.1f} lux → 需要开灯")
        lamp_on()
    elif "turn-off" in acts:
        print(f"[{datetime.now():%H:%M:%S}] {lux_now:.1f} lux → 需要关灯")
        lamp_off()
    else:
        print(f"[{datetime.now():%H:%M:%S}] {lux_now:.1f} lux → 无动作")

def main_loop():
    while True:
        try:
            decide_and_act()
        except Exception as e:
            print(f"[ERR] {e}")
        time.sleep(10)

if __name__ == "__main__":
    main_loop()
