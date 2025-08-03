import subprocess, re, logging
from pathlib import Path
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

STEP_RE = re.compile(r"\(\s*([^) ]+)\s*", re.I)

def build_problem(lux_now: int):
    is_dark = lux_now < 100
    init_parts = ["(dark)" if is_dark else "(lamp-on)"]
    pddl = f"""
(define (problem light-problem)
  (:domain light-control)
  (:init {' '.join(init_parts)})
  (:goal (lamp-on))
)
""".strip()
    Path("problem.pddl").write_text(pddl)

def run_planner():
    # 1) 运行 BFS 搜索
    problem_file = "problem.pddl"
    cmd = ["python3", "-m", "pyperplan", "-s", "bfs", "domain.pddl", problem_file]
    out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)

    # 2) 先尝试读取  <problem.pddl>.soln
    soln_path = Path("problem.pddl" + ".soln")   # --> problem.pddl.soln
    actions = []
    for line in soln_path.read_text().splitlines():
        m = STEP_RE.search(line)      # 用 search，别用 match
        if m:
            actions.append(m.group(1).lower())

    # 3) 若文件不存在，再从 stdout 里抓（给以后换 A*、GBF 等留后门）
    if not actions:
        for line in out.splitlines():
            m = STEP_RE.search(line)
            if m:
                actions.append(m.group(1).lower())

    return actions


if __name__ == "__main__":
    lux_now = 80
    build_problem(lux_now)
    actions = run_planner()
    if "turn-on" in actions:
        print(">>> 执行动作：开灯")
    elif "turn-off" in actions:
        print(">>> 执行动作：关灯")
    else:
        print(">>> 无需动作")
