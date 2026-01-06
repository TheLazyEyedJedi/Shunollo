"""
bio_rhythm.py
-------------
"Digital Cardiology" - Using Shunollo Physics to detect Arrhythmia.

Domain: Health / Wearables
Concept: A healthy heart has "Variability" (Entropy) but stable "Rhythm" (Flux).
         A fibrillating heart has massive Flux (Chaos).
         A flatlining heart has Zero Entropy (Death).

Scenario: Detecting Atrial Fibrillation (AFib) from simulated R-R intervals.
"""
import sys
import os
import random

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from shunollo_core import physics
from shunollo_core.learning.synaptic_plasticity import train_neural_intuition, query_neural_intuition

def analyze_heartbeat(bpm, hrv, train_mode=False):
    # 1. PHYSICS OF LIFE
    # Entropy: How complex is the rhythm? (Healthy hearts are complex)
    # Flux: How unstable is the rate? (AFib is unstable)
    
    entropy_score = physics.calculate_entropy(random.randbytes(int(hrv * 10))) # Simulating complexity
    flux_score = physics.calculate_flux(variance=hrv)
    
    physics_profile = {
        "roughness": flux_score,     # Chaos
        "flux": flux_score,
        "viscosity": 0.1,
        "salience": bpm / 200.0,     # Intensity
        "dissonance": 0.1,
        "volatility": flux_score,
        "action": bpm / 180.0,       # Metabolic load
        "hamiltonian": bpm / 200.0, 
        "ewr": entropy_score,        # Complexity
        "harmony": 1.0 if not train_mode else 1.0
    }
    
    vector = physics.vectorize_sensation(physics_profile, protocol="bio")

    if train_mode:
        train_neural_intuition(vector, is_anomaly=False)
        return

    intuition = query_neural_intuition(vector)
    score = intuition["anomaly_score"]
    
    status = "Health"
    if score > 0.1: status = "ARRHYTHMIA"
    if bpm < 40: status = "BRADYCARDIA"
    
    print(f"[BPM: {bpm:3}] HRV: {hrv:4.1f}ms | Flux: {flux_score:.2f} | Status: {status} (Surprise: {score:.2f})")

def main():
    print("Initializing Shunollo Cardiology Core...")
    
    # 0. CHILDHOOD (Training on Healthy Adults)
    print(">>> Learning 'Sinus Rhythm'...")
    for _ in range(100):
        # Healthy: 60-100 BPM, 20-50ms HRV (Natural variability)
        analyze_heartbeat(random.randint(60, 90), random.uniform(20, 50), train_mode=True)
    print(">>> Baseline Established.\n")
    
    # 1. Normal Activity
    print("--- RESTING STATE ---")
    for _ in range(3):
        analyze_heartbeat(random.randint(65, 75), random.uniform(30, 40))

    # 2. AFib Event (Chaos)
    print("\n--- ATRIAL FIBRILLATION DETECTED ---")
    for _ in range(3):
        # AFib: Irregular beat (High HRV/Flux), Often Rapid
        analyze_heartbeat(random.randint(110, 160), random.uniform(100, 300))

if __name__ == "__main__":
    main()
