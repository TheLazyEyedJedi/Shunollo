"""
server_heat.py
--------------
"Thermodynamics of Compute" - Using Shunollo Physics to detect System Meltdown.

Domain: DevOps / SRE
Concept: A server is a thermodynamic engine.
         CPU Load = Action (Kinetic Energy).
         Latency  = Friction (Viscosity).
         
Scenario: Detecting a "Meltdown" (High Load + High Latency) vs "Efficiency" (High Load + Low Latency).
"""
import sys
import os
import random

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from shunollo_core import physics
from shunollo_core.learning.synaptic_plasticity import train_neural_intuition, query_neural_intuition

def analyze_server(cpu_percent, latency_ms, train_mode=False):
    # 1. PHYSICS OF COMPUTE
    # Action: How much work is happening? (CPU)
    # Hamiltonian: Total energy in system (CPU + RAM)
    # Viscosity: Resistance to flow (Latency)
    
    action = cpu_percent / 100.0
    viscosity = min(1.0, latency_ms / 1000.0) # >1s is extremely viscous
    
    # "Lagrangian Strain": When Action is high but Viscosity is also high.
    # Means lots of work but stuck in mud (Inefficiency/Thrashing).
    strain = action * viscosity 

    physics_profile = {
        "roughness": strain,         # Thrashing texture
        "flux": 0.1,
        "viscosity": viscosity,
        "salience": action,
        "dissonance": strain * 2.0,  # Pain
        "volatility": 0.1,
        "action": action,
        "hamiltonian": action, 
        "ewr": 0.0,
        "harmony": 1.0 # Default
    }
    
    vector = physics.vectorize_sensation(physics_profile, protocol="sys")

    if train_mode:
        train_neural_intuition(vector, is_anomaly=False)
        return

    intuition = query_neural_intuition(vector)
    score = intuition["anomaly_score"]
    
    status = "Optimal"
    if score > 0.1: status = "MELTDOWN"
    if cpu_percent > 90 and score < 0.1: status = "Heavy Load (Safe)"
    
    print(f"[CPU: {cpu_percent:3}%] Latency: {latency_ms:4}ms | Strain: {strain:.2f} | Status: {status} (Surprise: {score:.2f})")

def main():
    print("Initializing Shunollo SysAdmin Core...")
    
    # 0. CHILDHOOD (Training on Healthy Traffic)
    print(">>> Learning 'Golden Signals'...")
    for _ in range(200):
        # Healthy: Low/Med CPU, Low Latency
        cpu = random.randint(10, 80)
        lat = random.randint(5, 50) 
        analyze_server(cpu, lat, train_mode=True)
        
        # Healthy: High CPU, Low Latency (Efficient Scaling)
        # We must teach the brain that 'Working Hard' is okay if 'Friction' is low.
        analyze_server(random.randint(90, 99), random.randint(5, 50), train_mode=True)
        
    print(">>> Baseline Established.\n")
    
    # 1. Heavy but Healthy (Efficient Scaling)
    print("--- BLACK FRIDAY TRAFFIC (Efficient) ---")
    analyze_server(95, 45) # High CPU, but fast (Good!)
    analyze_server(98, 55)

    # 2. Database Lock / Thrashing (Meltdown)
    print("\n--- DEADLOCK DETECTED (Meltdown) ---")
    analyze_server(99, 2500) # High CPU AND High Latency (Bad!)
    analyze_server(100, 5000)

if __name__ == "__main__":
    main()
