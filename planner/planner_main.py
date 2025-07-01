import os
from influx_utils import get_current_luminance

def generate_problem_file(lux):
    # 若查询不到数据，采用保守策略：假设环境“dark”
    if lux is None:
        print("⚠️  Warning: No luminance data found, defaulting to 'dark'.")
        lux_status = "dark"
    else:
        lux_status = "dark" if lux < 300 else "bright"

    with open("problem.pddl", "w") as f:
        f.write(f"""
(define (problem light-control)
  (:domain lighting)

  (:objects light1)

  (:init
    ({lux_status})
    (off light1)
  )

  (:goal (on light1))
)
""")

def main():
    lux = get_current_luminance()
    print(f"🔍 Current Lux: {lux}")
    generate_problem_file(lux)
    # TODO: Call fast-downward and parse result

if __name__ == "__main__":
    main()
