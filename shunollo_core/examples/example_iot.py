"""
Example: IoT Predictive Maintenance
-----------------------------------
Demonstrates using Shunollo Core to detect mechanical failure precursors
in IoT sensor data using Roughness (Vibration) and Energy (Heat).

Concepts:
- Roughness: Vibration entropy (mechanical wear).
- Energy: Temperature output (overheating).
"""
import time
import random
import math
from typing import Dict, Any
from shunollo_core import physics
from shunollo_core.models import ShunolloSignal
from shunollo_core.interfaces import BaseTransducer, BaseAgent

class IoTTransducer(BaseTransducer):
    def ingest(self, reading: Dict[str, Any]) -> ShunolloSignal:
        temp = reading.get('temp_c', 0.0)
        vibration = reading.get('vibration_hz', 0.0)
        
        # 1. Physics: Energy (Heat output)
        # Normalized: 0C to 100C
        energy = min(1.0, temp / 100.0)
        
        # 2. Physics: Roughness (Vibration entropy)
        # Map vibration noise to entropy
        entropy = math.log2(vibration + 1.0)
        roughness = physics.calculate_roughness(entropy)
        
        return ShunolloSignal(
            energy=energy,
            roughness=roughness,
            harmony=1.0 - roughness, # High vibration = Low harmony
            timestamp=time.time(),
            source="sensor_array_1"
        )

class MaintenanceAgent(BaseAgent):
    def evaluate(self, signal: ShunolloSignal) -> bool:
        # High Roughness = Bearing failure imminent
        if signal.roughness > 0.6:
            print(f"[MAINTENANCE] Vibration detected! Roughness={signal.roughness:.2f}")
            return True
        return False

def main():
    print("Initializing Shunollo Core - IoT Example...")
    transducer = IoTTransducer()
    agent = MaintenanceAgent()
    
    print("Monitoring sensor array...")
    
    # Mock Stream
    readings = [
        {'temp_c': 45.0, 'vibration_hz': 2.0},   # Normal
        {'temp_c': 48.0, 'vibration_hz': 3.5},   # Slight wobble
        {'temp_c': 55.0, 'vibration_hz': 45.0},  # BEARING FAILING
        {'temp_c': 85.0, 'vibration_hz': 120.0}, # CRITICAL FAILURE
    ]
    
    for reading in readings:
        signal = transducer.ingest(reading)
        status = "[OK]  "
        if agent.evaluate(signal):
            status = "[FAIL]"
            
        print(f"{status} Temp={reading['temp_c']}C | Vib={reading['vibration_hz']}Hz")

if __name__ == "__main__":
    main()
