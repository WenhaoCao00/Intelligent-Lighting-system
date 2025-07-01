import subprocess, os, re, sys

PLANNER = "/app/downward/fast-downward.py"   # 容器内路径
DOMAIN  = "domain.pddl"
PROBLEM = "problem.pddl"

def run_planner():
    result = subprocess.run(
        [PLANNER, DOMAIN, PROBLEM,
         "--search", "lazy_greedy([ff()], preferred=[ff()])"],
        text=True, capture_output=True
    )

    actions = re.findall(r"^\s*\w.*\)", result.stdout, flags=re.MULTILINE)
    if any("turn-on" in act.lower() for act in actions):
        print("我准备开灯")
    else:
        print("不需要开灯")

if __name__ == "__main__":
    run_planner()
