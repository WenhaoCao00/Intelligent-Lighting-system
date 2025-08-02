from plugwise.api import *
from time import sleep
from datetime import datetime, timezone
DEFAULT_PORT = "/dev/ttyUSB0"
mac = "000D6F0005692B55"  # Circle+ MAC

stick = Stick(DEFAULT_PORT)
circle = Circle(mac, stick)

current_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
print(f"current time is: {current_time}")

circle.set_clock(current_time)      # ⬅ ③ 把规范化后的时间写进去
print(f"After setting up the plugwise time is: {circle.get_clock()}")
sleep(1)


# state = circle.get_info()
# print(state)

power_usage_history = circle.get_power_usage_history()
print(power_usage_history)
print("########################")
print(power_usage_history[0][1])

# if state["relay_state"] == 1:
#     power_usage = circle.get_power_usage()
#     print(power_usage)
#     print(type(power_usage))
# else:
#     print(0.0)
# # toggle switch
# if state["relay_state"] == 1:
#     print("Now turning off...")
#     circle.switch_off()
# else:
#     print("Now turning on...")
#     circle.switch_on()