import time
import math
from st3215 import ST3215
from dataclasses import dataclass
from enum import Enum

servo = ST3215('COM3')
sts_id = [1, 2, 3, 4, 5, 6, 7, 8]
acc = 250
speed = 2400

angle_limits = {
    1: (75, 150), 2: (30, 140), 3: (30, 105), 4: (40, 150),
    5: (30, 105), 6: (40, 150), 7: (85, 150), 8: (30, 140)
}

trims = {
    1: 100, 2: 60, 3: 140, 4: 55,
    5: 0, 6: 10, 7: 0, 8: 40}

SERVO_MAPPING = [
    (1, 'lf', 'x'), (2, 'lf', 'z'),  # Serwo 1: LF X, Serwo 2: LF Z
    (3, 'rf', 'x'), (4, 'rf', 'z'),  # Serwo 3: RF X, Serwo 4: RF Z
    (5, 'lr', 'x'), (6, 'lr', 'z'),  # Serwo 5: LR X, Serwo 6: LR Z
    (7, 'rr', 'x'), (8, 'rr', 'z')   # Serwo 7: RR X, Serwo 8: RR Z
]

NEUTRAL_ANGLES = {
    1: 100, 2: 90, 3: 80, 4: 90,
    5: 60, 6: 90, 7: 120, 8: 90
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
    """Parametry chodu dla każdej nogi (LF, RF, LR, RR)"""
    x_amps: tuple    # amplitudy ruchu w osi X
    z_amps: tuple    # amplitudy podnoszenia w osi Z
    x_offsets: tuple # offset pozycji spoczynkowej X
    z_offsets: tuple
    phase_offsets: tuple # przesunięcia fazowe

GAIT_CONFIGS = {
    GaitMode.CREEP_FORWARD: GaitParams(
        x_amps=(30, -30, 30, -30),      # LF, RF, LR, RR
        z_amps=(15, -15, -15, 15),
        x_offsets=(85, 95, 45, 135),
        z_offsets=(90, 90, 90, 90),
        phase_offsets=(0.00, 0.50, 0.25, 0.75)
    ),
    GaitMode.CREEP_BACKWARD: GaitParams(
        x_amps=(-30, 30, -30, 30),
        z_amps=(15, -15, -15, 30),
        x_offsets=(135, 45, 95, 85),
        z_offsets=(90, 90, 90, 90),
        phase_offsets=(0.25, 0.75, 0.00, 0.50)
    ),
    GaitMode.CREEP_RIGHT: GaitParams(
        x_amps=(30, 30, 30, 30),
        z_amps=(15, -15, -15, 15),
        x_offsets=(120, 30, 30, 120),        
        z_offsets=(90, 90, 90, 90),
        phase_offsets=(0.00, 0.50, 0.25, 0.75)
    ),
    GaitMode.CREEP_LEFT: GaitParams(
        x_amps=(-30, -30, -30, -30),
        z_amps=(15, -15, -15, 15),
        x_offsets=(150, 60, 60, 150),        
        z_offsets=(90, 90, 90, 90),
        phase_offsets=(0.00, 0.50, 0.25, 0.75)
    ),
    GaitMode.CREEP_TROT_FORWARD: GaitParams(
        x_amps=(30, -30, 30, -30),
        z_amps=(15, -15, -15, 15),
        x_offsets=(105, 75, 45, 135),
        z_offsets=(90, 90, 90, 90),
        phase_offsets=(0.50, 0.00, 0.00, 0.50)  # LF i LR w fazie, RF i RR w fazie
    ),
    GaitMode.CREEP_TROT_BACKWARD: GaitParams(
        x_amps=(-30, 30, -30, 30),
        z_amps=(15, -15, -15, 15),
        x_offsets=(135, 45, 75, 105),
        z_offsets=(90, 90, 90, 90),
        phase_offsets=(0.50, 0.00, 0.00, 0.50)  # LF i LR w fazie, RF i RR w fazie
    ),
    GaitMode.CREEP_TROT_RIGHT: GaitParams(
        x_amps=(-30, -30, -30, -30),
        z_amps=(15, -15, -15, 15),
        x_offsets=(135, 75, 75, 135),
        z_offsets=(90, 90, 90, 90),
        phase_offsets=(0.50, 0.00, 0.00, 0.50)  # LF i LR w fazie, RF i RR w fazie
    ),
    GaitMode.CREEP_TROT_LEFT: GaitParams(
        x_amps=(30, 30, 30, 30),
        z_amps=(15, -15, -15, 15),
        x_offsets=(105, 45, 45, 105),
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
    if step % 10 == 0:  # Wyświetlaj co 10 kroków żeby nie zaśmiecać
        print(f"Krok {step} | Czas: {t:.1f}s | Tryb: {mode.name} | ", end="")
        
        # Wyświetl wszystkie kąty w jednej linii
        leg_angles = []
        for leg in ['lf', 'rf', 'lr', 'rr']:
            x_angle = angles[leg]['x']
            z_angle = angles[leg]['z']
            leg_angles.append(f"{leg.upper()}: X={x_angle:6.1f}° Z={z_angle:6.1f}°")
        
        print(" | ".join(leg_angles))
        
def execute_gait(mode):
    t_cycle = 2.0  # czas pełnego cyklu chodu [s]
    dt = 0.05       # krok czasowy [s]
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

if __name__ == "__main__":
    # execute_gait(GaitMode.CREEP_FORWARD)
    # execute_gait(GaitMode.CREEP_LEFT)
    # execute_gait(GaitMode.CREEP_RIGHT)
    # execute_gait(GaitMode.CREEP_TROT_FORWARD)
    # execute_gait(GaitMode.CREEP_TROT_BACKWARD)
    # execute_gait(GaitMode.CREEP_TROT_RIGHT)  
    execute_gait(GaitMode.CREEP_TROT_LEFT)  