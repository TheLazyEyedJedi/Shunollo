"""
motor_decay.py
--------------
"Machine Empathy" - Using Shunollo Physics for Predictive Maintenance.

Domain: IoT / Manufacturing
Concept: Looking at vibration data from a motor.
         Smooth Rotation = Low Roughness.
         Bearing Grit/Rubbing = High Roughness (Texture).

Scenario: Detecting a "Bearing Failure" before it breaks.
"""
import sys
import os
import random

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from shunollo_core import physics
from shunollo_core.learning.synaptic_plasticity import train_neural_intuition, query_neural_intuition

def analyze_vibration(rpm, vibration_g, train_mode=False):
    # 1. PHYSICS OF MOTION
    # Energy: Kinetic Energy of rotation (RPM)
    # Roughness: The texture of the vibration (G-force variance)
    
    energy = min(1.0, rpm / 5000.0)
    roughness = min(1.0, vibration_g * 2.0) # >0.5g is rough
    
    physics_profile = {
        "roughness": roughness,      # The key metric
        "flux": roughness * 0.5,
        "viscosity": 0.05,           # Low friction (ideally)
        "salience": energy,
        "dissonance": roughness,     # Mechanical screaming
        "volatility": 0.0,
        "action": energy,
        "hamiltonian": energy, 
        "ewr": 0.0,
        "harmony": 1.0
    }
    
    vector = physics.vectorize_sensation(physics_profile, protocol="iot")

    if train_mode:
        train_neural_intuition(vector, is_anomaly=False)
        return

    intuition = query_neural_intuition(vector)
    score = intuition["anomaly_score"]
    
    status = "Smooth"
    if score > 0.1: status = "GRINDING"
    
    print(f"[RPM: {rpm:4}] Vib: {vibration_g:.2f}g | Roughness: {roughness:.2f} | Status: {status} (Surprise: {score:.2f})")

def main():
    print("Initializing Shunollo IoT Core...")
    
    # 0. CHILDHOOD (Training on Factory Calibration)
    print(">>> Learning 'Factory Smooth'...")
    for _ in range(100):
        # Good Motor: Varies in RPM, but vibration is always low
        rpm = random.randint(1000, 4000)
        vib = random.uniform(0.01, 0.05) # Smooth
        analyze_vibration(rpm, vib, train_mode=True)
    print(">>> Baseline Established.\n")
    
    # 1. Normal Operation
    print("--- SHIFT 1 (Normal) ---")
    analyze_vibration(3500, 0.04)
    analyze_vibration(4100, 0.06)

    # 2. Ball Bearing Failure (Grit)
    print("\n--- BEARING FAILURE IMMINENT ---")
    analyze_vibration(3450, 0.35) # High vibration
    analyze_vibration(3300, 0.72) # Very high

if __name__ == "__main__":
    main()
