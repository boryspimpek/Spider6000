import time
import math
from st3215 import ST3215

servo = ST3215('COM3')
sts_id = [1, 2, 3, 4, 5, 6, 7, 8]
acc = 250
speed = 2400

angle_limits = {
    1: (85, 115),
    2: (30, 140),
    3: (65, 95),
    4: (40, 150),
    5: (45, 75),
    6: (40, 150),   
    7: (105, 135),
    8: (30, 140)
}

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

for id in sts_id:
    servo.SetMode(id, 0)
    servo.SetAcceleration(id, acc)
    servo.SetSpeed(id, speed)

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
    servo.WritePosition(id, trimmed_pos)

def creep_gait(x_amp, z_amp, x_off, z_off, phase):
    # LIFT (0-25% cyklu)
    if phase < 0.25:
        z = z_amp * math.sin(phase / 0.25 * math.pi)
        x = x_off + x_amp * math.sin(phase / 0.25 * math.pi / 2)
    # RETURN (25-100% cyklu) 
    else:
        z = 0
        x = x_off + x_amp * math.cos((phase - 0.25) / 0.75 * math.pi / 2)
    
    return z, x

if __name__ == "__main__":
    t_cycle = 4.0  
    dt = 0.1       
    
    print("Krok | Czas  | LF-z    | LF-x    | RR-z   | RR-x    | RF-z   | RF-x    | LR-z   | LR-x")
    print("-" * 95)
    
    step = 0
    while True:
        t = step * dt
        phase = (t / t_cycle) % 1.0  # normalizacja do 0.0-1.0
        
        # Fazy dla każdej nogi
        lf_z, lf_x = creep_gait(30, 30, 85, 0, phase=(phase + 0.00) % 1.0)
        rr_z, rr_x = creep_gait(-30, 30, 135, 0, phase=(phase + 0.75) % 1.0)
        rf_z, rf_x = creep_gait(-30, 30, 95, 0, phase=(phase + 0.50) % 1.0)
        lr_z, lr_x = creep_gait(30, 30, 45, 0, phase=(phase + 0.25) % 1.0)
        
        print(f"{step:4d} | {t:4.1f}s | {lf_z:6.2f}° | {lf_x:6.2f}° | "
              f"{rr_z:6.2f}° | {rr_x:6.2f}° | {rf_z:6.2f}° | {rf_x:6.2f}° | "
              f"{lr_z:6.2f}° | {lr_x:6.2f}°")
        
        move_servo(1, lf_x)
        move_servo(2, lf_z)
        move_servo(3, rf_x)
        move_servo(4, rf_z)
        move_servo(5, lr_x)
        move_servo(6, lr_z)
        move_servo(7, rr_x)
        move_servo(8, rr_z)

        time.sleep(dt)
        step += 1