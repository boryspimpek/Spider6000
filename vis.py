import matplotlib.pyplot as plt
import numpy as np
import math

def creep_gait(x_amp, z_amp, x_off, z_off, phase):
    # LIFT (0-25% cyklu)
    if phase < 0.25:
        z = z_off + z_amp * math.sin(phase / 0.25 * math.pi)
        x = x_off + x_amp * math.sin(phase / 0.25 * math.pi / 2)
    # RETURN (25-100% cyklu) 
    else:
        z = z_off
        x = x_off + x_amp * math.cos((phase - 0.25) / 0.75 * math.pi / 2)
    
    return z, x

# Parametry symulacji
t_cycle = 2.0
dt = 0.02  # mniejszy krok czasu dla płynniejszego wykresu
total_time = 3 * t_cycle  # 3 pełne cykle

# Przygotowanie danych
time_points = np.arange(0, total_time, dt)
phases = (time_points / t_cycle) % 1.0

# Obliczenie pozycji dla lewej przedniej nogi (LF)
lf_z_positions = []
lf_x_positions = []

for phase in phases:
    z, x = creep_gait(30, 30, 85, 90, phase)
    lf_z_positions.append(z)
    lf_x_positions.append(x)

# Tworzenie wykresów
plt.figure(figsize=(12, 8))

# Wykres unoszenia (Z)
plt.subplot(2, 1, 1)
plt.plot(time_points, lf_z_positions, 'b-', linewidth=2, label='Unoszenie (Z)')
plt.title('Ruch nogi LF - Unoszenie i Przesuwanie', fontsize=14)
plt.ylabel('Kąt unoszenia [°]', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend()

# Zaznaczenie faz cyklu
plt.axvspan(0, t_cycle*0.25, alpha=0.2, color='red', label='Faza unoszenia')
plt.axvspan(t_cycle*0.25, t_cycle, alpha=0.2, color='green', label='Faza powrotu')
for i in range(3):
    plt.axvline(x=i*t_cycle, color='gray', linestyle='--', alpha=0.5)
    plt.axvline(x=i*t_cycle + 0.25*t_cycle, color='gray', linestyle=':', alpha=0.5)

# Wykres przesuwania (X)
plt.subplot(2, 1, 2)
plt.plot(time_points, lf_x_positions, 'r-', linewidth=2, label='Przesuwanie (X)')
plt.xlabel('Czas [s]', fontsize=12)
plt.ylabel('Kąt przesuwania [°]', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend()

# Zaznaczenie faz cyklu
plt.axvspan(0, t_cycle*0.25, alpha=0.2, color='red', label='Faza unoszenia')
plt.axvspan(t_cycle*0.25, t_cycle, alpha=0.2, color='green', label='Faza powrotu')
for i in range(3):
    plt.axvline(x=i*t_cycle, color='gray', linestyle='--', alpha=0.5)
    plt.axvline(x=i*t_cycle + 0.25*t_cycle, color='gray', linestyle=':', alpha=0.5)

plt.tight_layout()
plt.show()

# Dodatkowy wykres - obie składowe razem
plt.figure(figsize=(12, 6))
plt.plot(time_points, lf_z_positions, 'b-', linewidth=2, label='Unoszenie (Z)')
plt.plot(time_points, lf_x_positions, 'r-', linewidth=2, label='Przesuwanie (X)')
plt.title('Ruch nogi LF - Unoszenie i Przesuwanie (razem)', fontsize=14)
plt.xlabel('Czas [s]', fontsize=12)
plt.ylabel('Kąt [°]', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend()

# Zaznaczenie faz cyklu
plt.axvspan(0, t_cycle*0.25, alpha=0.2, color='orange', label='Faza unoszenia')
plt.axvspan(t_cycle*0.25, t_cycle, alpha=0.2, color='lightblue', label='Faza powrotu')
for i in range(3):
    plt.axvline(x=i*t_cycle, color='gray', linestyle='--', alpha=0.5, label='Początek cyklu' if i==0 else "")
    plt.axvline(x=i*t_cycle + 0.25*t_cycle, color='gray', linestyle=':', alpha=0.5, label='Koniec unoszenia' if i==0 else "")

plt.tight_layout()
plt.show()

# Tabela z przykładowymi wartościami
print("\nPrzykładowe wartości dla jednego cyklu:")
print("Czas [s] | Faza  | LF-Z [°] | LF-X [°]")
print("-" * 40)
for t in np.arange(0, t_cycle + 0.1, 0.2):
    phase = (t / t_cycle) % 1.0
    z, x = creep_gait(30, 30, 85, 90, phase)
    phase_name = "UNOSZENIE" if phase < 0.25 else "POWRÓT"
    print(f"{t:7.1f} | {phase_name:8} | {z:8.2f} | {x:8.2f}")