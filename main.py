import time
import math
from st3215 import ST3215


#  Servos:
#   _________   ________   _________
#  |(2)______)(1)      (3)(______(4)|
#  |__|       |   KAME   |       |__|
#             |          |
#             |          |
#             |          |
#   _________ |          | _________
#  |(6)______)(5)______(7)(______(8)|
#  |__|                          |__|

servo = ST3215('COM3')
sts_id = [1, 2, 3, 4, 5, 6, 7, 8]
acc = 250
speed = 2400

for id in sts_id:
    servo.SetMode(id, 0)
    servo.SetAcceleration(id, acc)
    servo.SetSpeed(id, speed)

def creep_gait(x_amp, z_amp, t_cycle, t_elapsed, phase=0):
    t_full = 4 * t_cycle
    progress = (t_elapsed % t_full) / t_full
    p = (progress + phase) % 1.0
    
    # LIFT
    z = z_amp * math.sin(math.pi * p / 0.25) if p < 0.25 else 0
    
    # HORIZONTAL
    if p < 0.25:
        x = x_amp * math.sin((p / 0.25) * math.pi / 2)
    else:
        x = x_amp * math.cos(((p - 0.25) / 0.75) * math.pi / 2)
    
    return z, x

if __name__ == "__main__":
    t0 = time.time()
    t_cycle = 1.0
    
    print("Time  | LF-z    | LF-x    | RR-z   | RR-x    | RF-z   | RF-x    | LR-z   | LR-x")
    print("-" * 85)
    
    for i in range(45):
        t = time.time() - t0
        t_target = i * 0.1
        
        if t < t_target:
            time.sleep(t_target - t)
            t = t_target
        
        lf_z, lf_x = creep_gait(40, 30, t_cycle, t, phase=0.0)
        rr_z, rr_x = creep_gait(40, 30, t_cycle, t, phase=0.75)
        rf_z, rf_x = creep_gait(40, 30, t_cycle, t, phase=0.5)
        lr_z, lr_x = creep_gait(40, 30, t_cycle, t, phase=0.25)
        
        print(f"{t:4.1f}s |  {lf_z:5.1f}° | {lf_x:6.1f}° | "
              f"{rr_z:5.1f}° | {rr_x:6.1f}° | {rf_z:5.1f}° | {rf_x:6.1f}° | "
              f"{lr_z:5.1f}° | {lr_x:6.1f}°")
        
        servo.WritePosition(1, servo.rad_to_servo(lf_x))
        servo.WritePosition(2, servo.rad_to_servo(lf_z))
        servo.WritePosition(3, servo.rad_to_servo(rf_x))
        servo.WritePosition(4, servo.rad_to_servo(rf_z))
        servo.WritePosition(5, servo.rad_to_servo(lr_x))
        servo.WritePosition(6, servo.rad_to_servo(lr_z))
        servo.WritePosition(7, servo.rad_to_servo(rr_x))
        servo.WritePosition(8, servo.rad_to_servo(rr_z))

        time.sleep(0.1)
