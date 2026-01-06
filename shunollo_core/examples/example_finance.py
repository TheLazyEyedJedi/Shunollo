"""
Example: Financial Fraud Detection
----------------------------------
Demonstrates using Shunollo Core to detect market anomalies and fraud
using Energy (Volume) and Volatility (Price Fluctuation).

Concepts:
- Energy: Transaction size relative to history.
- Volatility: Price changes over time.
- Harmony: Consistency with user's typical behavior.
"""
import time
import random
from typing import Dict, Any
from shunollo_core import physics
from shunollo_core.models import ShunolloSignal
from shunollo_core.interfaces import BaseTransducer, BaseAgent

class FinancialTransducer(BaseTransducer):
    def ingest(self, txn: Dict[str, Any]) -> ShunolloSignal:
        amount = txn.get('amount', 0.0)
        baseline = txn.get('avg_amount', 100.0)
        
        # 1. Physics: Energy (Magnitude of transaction)
        # Normalized against baseline (criticality)
        energy = physics.calculate_energy(amount, criticality=1.0)
        
        # 2. Physics: Volatility (Price Instability)
        # Using simple size variance for demo
        volatility = physics.calculate_volatility_index(amount, baseline, sigma=20.0)
        
        return ShunolloSignal(
            energy=energy,
            roughness=volatility, # Map volatility to roughness
            harmony=1.0 if energy < 0.8 else 0.4,
            timestamp=time.time(),
            source="payment_gateway"
        )

class FraudAgent(BaseAgent):
    def evaluate(self, signal: ShunolloSignal) -> bool:
        # High Energy + High Volatility = Probable Fraud
        if signal.energy > 0.8 and signal.roughness > 0.7:
            print(f"[FRAUD ALERT] High Value (${signal.energy:.2f}) & Erratic ({signal.roughness:.2f})")
            return True
        return False

def main():
    print("Initializing Shunollo Core - Finance Example...")
    transducer = FinancialTransducer()
    agent = FraudAgent()
    
    print("Processing transactions...")
    
    # Mock Stream
    transactions = [
        {'amount': 50.0, 'avg_amount': 60.0},   # Normal
        {'amount': 1200.0, 'avg_amount': 60.0}, # Spike (Fraud?)
        {'amount': 55.0, 'avg_amount': 60.0},   # Normal
        {'amount': 5000.0, 'avg_amount': 60.0}, # Huge Spike (Fraud!)
    ]
    
    for i, txn in enumerate(transactions):
        signal = transducer.ingest(txn)
        is_fraud = agent.evaluate(signal)
        status = "[BLOCKED]" if is_fraud else "[CLEARED]"
        print(f"{status} Amt=${txn['amount']} -> Energy={signal.energy:.2f}")

if __name__ == "__main__":
    main()
