import keyboard  # pip install keyboard
from st3215 import ST3215
import time

servo = ST3215('COM3')

# Lista ID serw
sts_id = [1, 2, 3, 4, 5, 6, 7, 8]

# Mapowanie klawiszy do serw
# Każde serwo ma dwa klawisze: (w lewo, w prawo)
servo_keys = {
    1: ('q', 'a'),
    2: ('w', 's'),
    3: ('e', 'd'),
    4: ('r', 'f'),
    5: ('t', 'g'),
    6: ('y', 'h'),
    7: ('u', 'j'),
    8: ('i', 'k'),
}

STEP = 5  # krok ruchu
SPEED = 200
ACC = 10

angle_limits = {
    1: (0, 90), 2: (30, 140), 3: (90, 180), 4: (40, 150),
    5: (90, 180), 6: (40, 150), 7: (0, 90), 8: (30, 140)
}

trims = {
    1: -25, 2: 10, 3: 30, 4: 0,
    5: -15, 6: 0, 7: -10, 8: 60}

# Pozycje startowe wszystkich serw
positions = {sid: 90 for sid in sts_id}
initial_positions = positions.copy()

for id in sts_id:
    try:
        servo.SetMode(id, 0)
        servo.SetAcceleration(id, ACC)
        servo.SetSpeed(id, SPEED)
    except Exception as e:
        print(f"Error initializing servo {id}: {e}")

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

def center_all_servos():
    print("Ustawiam wszystkie serwa na 90")
    for sid in sts_id:
        move_servo(sid, 90)
        time.sleep(1)
    print("Gotowe! Wszystkie serwa są w pozycji neutralnej.\n")

def move():
    print("Sterowanie:")
    for sid, (left, right) in servo_keys.items():
        print(f"Serwo {sid}: {left} / {right}")
    print("Naciśnij 'x', aby zakończyć.\n")

    while True:
        for sid, (left, right) in servo_keys.items():
            if keyboard.is_pressed(left):
                positions[sid] = max(angle_limits[sid][0], positions[sid] - STEP)
                move_servo(sid, positions[sid])
                print(f"Serwo {sid}: {positions[sid]}")
                time.sleep(0.1)

            elif keyboard.is_pressed(right):
                positions[sid] = min(angle_limits[sid][1], positions[sid] + STEP)
                move_servo(sid, positions[sid])
                print(f"Serwo {sid}: {positions[sid]}")
                time.sleep(0.1)

        if keyboard.is_pressed('x'):
            print("\nZakończono.\n")
            break

    print("📋 Podsumowanie:")
    for sid in sts_id:
        print(f"Serwo {sid} (końcowa pozycja: {positions[sid]})")


if __name__ == "__main__":
    center_all_servos()
    move()
