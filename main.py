import time
import math
from st3215 import ST3215
from dataclasses import dataclass
from enum import Enum

servo = ST3215('COM3')
sts_id = [1, 2, 3, 4, 5, 6, 7, 8]
acc = 250
speed = 2400

h = 20                      # height
x_amp = 30                  # x amplitude
z_amp = 15                  # z amplitude
offset_front = 0            # front leg offset
offset_back = 45            # back legs offset

angle_limits = {
    1: (0, 90), 2: (30, 140), 3: (90, 180), 4: (40, 150),
    5: (90, 180), 6: (40, 150), 7: (0, 90), 8: (30, 140)
}

trims = {
    1: -25, 2: 10, 3: 30, 4: 0,
    5: -15, 6: 0, 7: -10, 8: 60}

SERVO_MAPPING = [
    (1, 'lf', 'x'), (2, 'lf', 'z'),  # Serwo 1: LF X, Serwo 2: LF Z
    (3, 'rf', 'x'), (4, 'rf', 'z'),  # Serwo 3: RF X, Serwo 4: RF Z
    (5, 'lr', 'x'), (6, 'lr', 'z'),  # Serwo 5: LR X, Serwo 6: LR Z
    (7, 'rr', 'x'), (8, 'rr', 'z')   # Serwo 7: RR X, Serwo 8: RR Z
]

NEUTRAL_ANGLES = {
    1: 45, 2: 90 - h, 3: 135, 4: 90 + h,
    5: 135, 6: 90 + h, 7: 45, 8: 90 - h
}

FORWARD_POS = {
    1: 90, 2: 90-h, 3: 110, 4: 90+h,
    5: 105, 6: 90+h, 7: 55, 8: 90-h
}

BACKWARD_POS = {
    1: 75, 2: 90-h, 3: 125, 4: 90+h,
    5: 90, 6: 90+h, 7: 70, 8: 90-h
}

LEFT_POS = {
    1: 30, 2: 90-h, 3: 140, 4: 90+h,
    5: 150, 6: 90+h, 7: 40, 8: 90-h
}

RIGHT_POS = {
    1: 60, 2: 90-h, 3: 130, 4: 90+h,
    5: 120, 6: 90+h, 7: 50, 8: 90-h
}

for id in sts_id:
    try:
        servo.SetMode(id, 0)
        servo.SetAcceleration(id, acc)
        servo.SetSpeed(id, speed)
    except Exception as e:
        print(f"Error initializing servo {id}: {e}")

class GaitMode(Enum):
    CREEP_FORWARD = 1
    CREEP_BACKWARD = 2
    CREEP_LEFT = 3
    CREEP_RIGHT = 4
    CREEP_TROT_FORWARD = 5
    CREEP_TROT_BACKWARD = 6
    CREEP_TROT_RIGHT = 7
    CREEP_TROT_LEFT = 8

@dataclass
class GaitParams:
    x_amps: tuple    
    z_amps: tuple    
    x_offsets: tuple 
    z_offsets: tuple
    phase_offsets: tuple 

GAIT_CONFIGS = {
    GaitMode.CREEP_FORWARD: GaitParams(
        x_amps=(-x_amp, x_amp, -x_amp, x_amp),      # LF, RF, LR, RR
        z_amps=(z_amp, -z_amp, -z_amp, z_amp),
        x_offsets=(90 - offset_front, 90 + offset_front, 90 + offset_back, 90 - offset_back),
        z_offsets=(90-h, 90+h, 90+h, 90-h),
        phase_offsets=(0.00, 0.50, 0.25, 0.75)
    ),
    GaitMode.CREEP_BACKWARD: GaitParams(
        x_amps=(x_amp, -x_amp, x_amp, -x_amp),
        z_amps=(z_amp, -z_amp, -z_amp, z_amp),
        x_offsets=(90 - offset_back, 90 + offset_back, 90 + offset_front, 90 - offset_front),
        z_offsets=(90-h, 90+h, 90+h, 90-h),
        phase_offsets=(0.25, 0.75, 0.00, 0.50)
    ),
    GaitMode.CREEP_LEFT: GaitParams(
        x_amps=(x_amp, x_amp, x_amp, x_amp),
        z_amps=(z_amp, -z_amp, -z_amp, z_amp),
        x_offsets=(45-x_amp/2, 135-x_amp/2, 135-x_amp/2, 45-x_amp/2),        
        z_offsets=(90-h, 90+h, 90+h, 90-h),
        phase_offsets=(0.00, 0.50, 0.25, 0.75)
    ),
    GaitMode.CREEP_RIGHT: GaitParams(
        x_amps=(-x_amp, -x_amp, -x_amp, -x_amp),
        z_amps=(z_amp, -z_amp, -z_amp, z_amp),
        x_offsets=(45+x_amp/2, 135+x_amp/2, 135+x_amp/2, 45+x_amp/2),        
        z_offsets=(90-h, 90+h, 90+h, 90-h),
        phase_offsets=(0.00, 0.50, 0.25, 0.75)
    ),
    GaitMode.CREEP_TROT_FORWARD: GaitParams(
        x_amps=(-x_amp, x_amp, -x_amp, x_amp),
        z_amps=(z_amp, -z_amp, -z_amp, z_amp),
        x_offsets=(45+x_amp/2, 135-x_amp/2, 135+x_amp/2, 45-x_amp/2),
        z_offsets=(90-h, 90+h, 90+h, 90-h),
        phase_offsets=(0.50, 0.00, 0.00, 0.50) 
    ),
    GaitMode.CREEP_TROT_BACKWARD: GaitParams(
        x_amps=(x_amp, -x_amp, x_amp, -x_amp),
        z_amps=(z_amp, -z_amp, -z_amp, z_amp),
        x_offsets=(45-x_amp/2, 135+x_amp/2, 135-x_amp/2, 45+x_amp/2),
        z_offsets=(90-h, 90+h, 90+h, 90-h),
        phase_offsets=(0.50, 0.00, 0.00, 0.50)  # LF i LR w fazie, RF i RR w fazie
    ),
    GaitMode.CREEP_TROT_RIGHT: GaitParams(
        x_amps=(-30, -30, -30, -30),
        z_amps=(15, -15, -15, 15),
        x_offsets=(45+x_amp/2, 135+x_amp/2, 135+x_amp/2, 45+x_amp/2),
        z_offsets=(90, 90, 90, 90),
        phase_offsets=(0.50, 0.00, 0.00, 0.50)  # LF i LR w fazie, RF i RR w fazie
    ),
    GaitMode.CREEP_TROT_LEFT: GaitParams(
        x_amps=(30, 30, 30, 30),
        z_amps=(15, -15, -15, 15),
        x_offsets=(45-x_amp/2, 135-x_amp/2, 135-x_amp/2, 45-x_amp/2),
        z_offsets=(90, 90, 90, 90),
        phase_offsets=(0.50, 0.00, 0.00, 0.50)  # LF i LR w fazie, RF i RR w fazie
    )
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
    try:
        safe_angle = check_angle_limit(id, angle_deg)
        pos = servo.angle_deg_to_servo(safe_angle)
        trimmed_pos = pos + trims.get(id, 0)
        servo.WritePosition(id, trimmed_pos)
    except Exception as e:
        print(f"Error moving servo {id}: {e}")

def return_to_neutral():
    for servo_id, angle in NEUTRAL_ANGLES.items():
        move_servo(servo_id, angle)
    
    time.sleep(1)
    print("All servos in neutral position")

def creep_gait(x_amp, z_amp, x_off, z_off, phase):
    # LIFT (0-25% cyklu)
    if phase < 0.25:
        z = z_off + z_amp * math.sin(phase / 0.25 * math.pi)
        x = x_off + x_amp * math.sin(phase / 0.25 * math.pi / 2)
    # RETURN (25-100% cyklu) 
    else:
        z = z_off  # noga na ziemi
        normalized_return_phase = (phase - 0.25) / 0.75
        x = x_off + x_amp * (1 - normalized_return_phase)  # liniowy powrót
    return z, x

def trot_gait(x_amp, z_amp, x_off, z_off, phase):
    if phase < 0.5:
        z = z_off + z_amp * math.sin(phase * 2 * math.pi)
        x = x_off + x_amp * math.sin(phase * math.pi)
    else:
        z = z_off
        x = x_off + x_amp * math.cos((phase - 0.5) * math.pi)
    
    return z, x

def calculate_gait_angles(mode, phase):
    params = GAIT_CONFIGS[mode]
    
    legs = ['lf', 'rf', 'lr', 'rr']
    angles = {}
    
    for i, leg in enumerate(legs):
        z, x = creep_gait(
            params.x_amps[i],
            params.z_amps[i], 
            params.x_offsets[i],
            params.z_offsets[i],
            phase=(phase + params.phase_offsets[i]) % 1.0
        )
        angles[leg] = {'x': x, 'z': z}
    
    return angles

def print_gait_info(step, t, angles, mode):
    if step % 5 == 0:  
        print(f"Krok {step} | Czas: {t:.1f}s | Tryb: {mode.name} | ", end="")
        
        leg_angles = []
        for leg in ['lf', 'rf', 'lr', 'rr']:
            x_angle = angles[leg]['x']
            z_angle = angles[leg]['z']
            leg_angles.append(f"{leg.upper()}: X={x_angle:6.1f}° Z={z_angle:6.1f}°")
        
        print(" | ".join(leg_angles))

def hello():
    HELLO_POS = {
    1: 45, 2: 30, 3: 135, 4: 150,
    5: 105, 6: 70, 7: 75, 8: 110}

    for servo_id, angle in HELLO_POS.items():
        move_servo(servo_id, angle)
    time.sleep(0.5)
    move_servo(2, 90)

    for _ in range(2):
        move_servo(1, 10)
        time.sleep(0.5)

        move_servo(1, 60)
        time.sleep(0.5)
    time.sleep(0.5)
    return_to_neutral()

def pushupOneLeg():
    PUSHUP_POS = {
    1: 90, 2: 90, 3: 90, 4: 90,
    5: 135, 6: 110, 7: 45, 8: 70}

    for servo_id, angle in PUSHUP_POS.items():
        move_servo(servo_id, angle)

    for _ in range(3):
        move_servo(2, 90)
        time.sleep(0.7)

        move_servo(2, 30)
        time.sleep(0.7)
    move_servo(2, 90)

    for _ in range(3):
        move_servo(4, 90)
        time.sleep(0.7)

        move_servo(4, 150)
        time.sleep(0.7)
    return_to_neutral()

def pushup():
    PUSHUP_POS = {
    1: 90, 2: 90, 3: 90, 4: 90,
    5: 135, 6: 110, 7: 45, 8: 70}

    for servo_id, angle in PUSHUP_POS.items():
        move_servo(servo_id, angle)

    for _ in range(3):
        move_servo(2, 90)
        move_servo(4, 90)
        time.sleep(0.7)

        move_servo(2, 30)
        move_servo(4, 150)
        time.sleep(0.7)
    return_to_neutral()

def execute_gait(mode):
    t_cycle = 1               # czas pełnego cyklu chodu [s]
    dt = 0.05                   # krok czasowy [s]
    step = 0
    
    try:
        while True:
            t = step * dt
            phase = (t / t_cycle) % 1.0  # normalizacja fazy do 0.0-1.0

            angles = calculate_gait_angles(mode, phase)
            
            # Użyj globalnego mapping serw
            for servo_id, leg, axis in SERVO_MAPPING:
                angle = angles[leg][axis]
                move_servo(servo_id, angle)
            
            print_gait_info(step, t, angles, mode)
            time.sleep(dt)
            step += 1
            
    except KeyboardInterrupt:
        print("\nGait interrupted by user")
        return_to_neutral()
    finally:
        print("Gait execution completed")

def prepareCreepForward():
    for servo_id, angle in FORWARD_POS.items():
        move_servo(servo_id, angle)
    time.sleep(0.5)

def prepareCreepBackward():
    for servo_id, angle in BACKWARD_POS.items():
        move_servo(servo_id, angle)
    time.sleep(0.5)

def prepareCreepLeft():
    for servo_id, angle in LEFT_POS.items():
        move_servo(servo_id, angle)
    time.sleep(0.2)

def prepareCreepRight():
    for servo_id, angle in RIGHT_POS.items():
        move_servo(servo_id, angle)
    time.sleep(0.2)

if __name__ == "__main__":
    # execute_gait(GaitMode.CREEP_FORWARD)
    # execute_gait(GaitMode.CREEP_BACKWARD)
    # execute_gait(GaitMode.CREEP_RIGHT)
    # execute_gait(GaitMode.CREEP_LEFT)
    # execute_gait(GaitMode.CREEP_TROT_FORWARD)
    # execute_gait(GaitMode.CREEP_TROT_BACKWARD)
    # execute_gait(GaitMode.CREEP_TROT_RIGHT)  
    # execute_gait(GaitMode.CREEP_TROT_LEFT)  

    # for servo_id, angle in BACKWARD_POS.items():
    #     move_servo(servo_id, angle)
    # time.sleep(1)
    # execute_gait(GaitMode.CREEP_BACKWARD)

    # prepareCreepBACKWARD()
    # execute_gait(GaitMode.CREEP_BACKWARD)

    # prepareCreepForward()
    # execute_gait(GaitMode.CREEP_FORWARD)

    # prepareCreepLeft()
    # execute_gait(GaitMode.CREEP_LEFT)

    # prepareCreepRight()
    # execute_gait(GaitMode.CREEP_RIGHT)

    # volt = servo.ReadVoltage(1)
    # print(volt)

    hello()
