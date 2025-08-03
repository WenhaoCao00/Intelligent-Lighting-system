"""智能灯光控制主程序

每 10 秒读取一次当前光照值 (lux)，
根据阈值自动规划并执行开/关灯动作。

依赖:
- pyperplan  (pip install pyperplan)
- influx_utils.get_current_luminance  ← 你自己的实现
- domain.pddl                       ← 与本文件同目录，见配套示例
"""

from __future__ import annotations

import logging
import re
import subprocess
import time
from pathlib import Path

from influx_utils import get_current_luminance  # 每 10 秒返回一次 lux 浮点值

# ================== 参数区 ==================
LOW_THRESHOLD = 100     # lux < 100  → 太暗，开灯
HIGH_THRESHOLD = 300    # lux > 300  → 太亮，关灯
CHECK_INTERVAL = 10     # 秒

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

def run_planner() -> list[str]:
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

    actions: list[str] = []

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

# ================ 执行动作 =================

def act(actions: list[str]) -> None:
    if "turn-on" in actions:
        logging.info(">>> 执行动作：开灯")
        # TODO: 在此调用 GPIO / HTTP / MQTT 等接口真正开灯
    elif "turn-off" in actions:
        logging.info(">>> 执行动作：关灯")
        # TODO: 在此调用硬件接口关灯
    else:
        logging.info(">>> Planner 给出零动作，无需操作")

# =================== 主循环 ==================

def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    try:
        while True:
            lux = float(get_current_luminance())
            logging.info("当前光照: %.2f lux", lux)

            if build_problem(lux):
                actions = run_planner()
                act(actions)
            else:
                logging.info("光照处于 [%d, %d] lux 范围，跳过动作。", LOW_THRESHOLD, HIGH_THRESHOLD)

            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\n已手动终止智能灯光控制程序。")


if __name__ == "__main__":
    main()
