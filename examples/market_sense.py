"""
market_sense.py
---------------
"Financial Proprioception" - Using Shunollo Physics to detect Market Anomalies.

This example demonstrates the "Financial Isomorphism":
- Stock Price     -> Energy (Hamiltonian)
- Volatility      -> Roughness (Texture)
- Volume          -> Kinetic (Mass)
- Market Drift    -> Flux (Directional Stability)

Scenario: Detecting a "Pump and Dump" scheme without knowing the specific asset.
"""
import sys
import os
import random
import time

# Add parent directory to path to find shunollo_core if not installed via pip
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from shunollo_core import physics
from shunollo_core.brain.autoencoder import get_imagination
from shunollo_core.learning.synaptic_plasticity import train_neural_intuition, query_neural_intuition

def generate_market_tick(mode="stable"):
    """
    Simulates a single market tick (price/volume).
    modes:
        stable: Random Walk (Brownian Motion)
        manipulated: High Flux + High Volatility (Pump & Dump)
    """
    if mode == "stable":
        # Safe asset: Low Volatility, Steady Volume
        price_change = random.uniform(-0.5, 0.5)
        volume = random.uniform(100, 200)
        volatility = 0.1
    else:
        # Manipulation: Excessive Volatility, Spiking Volume
        price_change = random.uniform(-5.0, 15.0) # Chaotic Upward Drift
        volume = random.uniform(1000, 5000) # Whales entering
        volatility = 0.9

    return {
        "price_delta": price_change,
        "volume": volume,
        "volatility": volatility,
        "tick_rate": 10 if mode == "stable" else 100 # HFT burst
    }

def analyze_tick(ticker: str, tick_data: dict, train_mode: bool = False):
    # 1. THE PHYSICS OF MONEY
    # Map Financial metrics to Physics
    
    # Energy: Magnitude of price action relative to volume
    # E = 1/2 * m * v^2
    energy = physics.calculate_energy(
        size=tick_data["volume"], 
        rate_hz=abs(tick_data["price_delta"]) * 10 
    )
    
    # Roughness: The texture of the volatility
    roughness = tick_data["volatility"] # Direct mapping
    
    # Flux: The directional instability (Jitter)
    flux = physics.calculate_flux(
        variance=tick_data["tick_rate"]
    )
    
    # 2. SOMATIC VECTOR (The "Feeling" of the Market)
    physics_profile = {
        "roughness": roughness,
        "flux": flux,
        "viscosity": 0.5, # Market Liquidity (Constant for demo)
        "salience": min(1.0, energy),
        "dissonance": roughness * flux, # Complexity
        "volatility": roughness,
        "action": min(1.0, tick_data["volume"] / 5000),
        "hamiltonian": min(1.0, energy), 
        "ewr": 0.0,
        "harmony": 1.0 if not train_mode else 1.0 # Default
    }
    
    # Protocol "market" allows the Brain to context-switch
    vector = physics.vectorize_sensation(physics_profile, protocol="market")
    
    if train_mode:
        # Teach the Brain: "This is what a healthy market feels like"
        train_neural_intuition(vector, is_anomaly=False)
        return

    # 3. NEURAL INTUITION
    intuition = query_neural_intuition(vector)
    anom_score = intuition["anomaly_score"]
    
    status = "NON-RANDOM" if anom_score > 0.1 else "Random Walk"
    print(f"[{ticker}] Px:{tick_data['price_delta']:>5.2f} | Vol:{tick_data['volume']:>4.0f} | Feel:{status} (Surprise: {anom_score:.2f})")

def main():
    print("Initializing Shunollo Financial Core...")
    
    # 0. The Childhood (Pre-Training Phase)
    print(">>> Learning 'Efficient Market Hypothesis' (Training)...")
    for _ in range(100):
        tick = generate_market_tick(mode="stable")
        analyze_tick("TRAIN", tick, train_mode=True)
    print(">>> Baseline Established.\n")
    
    # 1. Market Open: Stable Trading
    print("--- MARKET OPEN (09:30) ---")
    for _ in range(3):
        tick = generate_market_tick(mode="stable")
        analyze_tick("AAPL", tick)
        time.sleep(0.1)
        
    # 2. Flash Crash / Pump
    print("\n--- WHALE DETECTED (10:00) ---")
    for _ in range(3):
        tick = generate_market_tick(mode="manipulated")
        analyze_tick("GME ", tick) # High Volatility
        time.sleep(0.1)

if __name__ == "__main__":
    main()
