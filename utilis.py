import time
import math
from st3215 import ST3215


servo = ST3215('COM3')

###################################################### SETTING SECTION #################

######################## List servos
# print(servos := servo.ListServos())

######################## Ping servo
# print(alive := servo.PingServo(1))

######################## Change ID of servo
# servo.ChangeId(1, 8)
# time.sleep(1)
# print(servos := servo.ListServos())

####################### Define middle point
# id = 4
# servo.DefineMiddle(id)
# time.sleep(5)
# print(position := servo.ReadPosition(id))

# print(position := servo.ReadPosition(4))


# servo.MoveTo(7, 1024, 200, 10, True)
import math

ids = [1, 2, 3, 4, 5, 6, 7, 8]
acc = 250
speed = 2400

trims = {
    1: 100,
    2: 40,
    3: 140,
    4: 75,
    5: 0,
    6: 10,
    7: 0,
    8: 40
}

angle_limits = {
    1: (85, 115),
    2: (30, 140),
    3: (65, 95),
    4: (40, 150),
    5: (45, 75),
    6: (40, 150),   # poprawione!
    7: (105, 135),
    8: (30, 140)
}

standart = {
    1: 100,
    2: 90,
    3: 80,
    4: 90,
    5: 60,
    6: 90,
    7: 120,
    8: 90
}

def check_angle_limit(id, angle_deg):
    min_angle, max_angle = angle_limits.get(id, (-180, 180))
    if angle_deg < min_angle:
        print(f"⚠️ Servo {id}: kąt {angle_deg}° poniżej minimum ({min_angle}°) — ograniczono.")
        angle_deg = min_angle
    elif angle_deg > max_angle:
        print(f"⚠️ Servo {id}: kąt {angle_deg}° powyżej maksimum ({max_angle}°) — ograniczono.")
        angle_deg = max_angle
    return angle_deg

def move_servo(id, angle_deg):
    safe_angle = check_angle_limit(id, angle_deg)
    pos = servo.angle_deg_to_servo(safe_angle)
    trimmed_pos = pos + trims.get(id, 0)
    servo.WritePosition(id, trimmed_pos)  # zakładamy, że servo to Twój sterownik

for id, angle_deg in standart.items():
    move_servo(id, angle_deg)
