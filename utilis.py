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


servo.MoveTo(1, 1024, 200, 10, True)
servo.MoveTo(2, 1024, 200, 10, True)
servo.MoveTo(3, 1024, 200, 10, True)
servo.MoveTo(4, 1024, 200, 10, True)
servo.MoveTo(5, 1024, 200, 10, True)
servo.MoveTo(6, 1024, 200, 10, True)
servo.MoveTo(7, 1024, 200, 10, True)
servo.MoveTo(8, 1024, 200, 10, True)
