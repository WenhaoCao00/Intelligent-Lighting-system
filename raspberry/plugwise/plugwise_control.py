from plugwise.api import *
from datetime import datetime
DEFAULT_PORT = "/dev/ttyUSB0"
circle_plus_mac = "000D6F0005692B55" #circle+ 
circle_mac = "000D6F0004B1E6C4" #circle
stick = Stick(DEFAULT_PORT)
circle = Circle(circle_plus_mac, stick)
circle.switch_on() 

# current_time = datetime.now()
# circle.set_clock(current_time)
print(circle.get_clock())
print(circle.get_power_usage_history())
