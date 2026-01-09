import time
import numpy as np
import pytest
from shunollo_core.physics.mechanics import calculate_energy, calculate_entropy, calculate_roughness
from shunollo_core.physics.thermo import ThermodynamicSystem
from shunollo_core.cognition.active_inference import ActiveInferenceAgent
from shunollo_core.memory.holographic import HolographicMemory
from shunollo_core.brain.autoencoder import Autoencoder

@pytest.fixture
def agent():
    return ActiveInferenceAgent()

@pytest.fixture
def memory():
    return HolographicMemory(size=1024)

def test_physics_calculation_latency():
    """Benchmark raw physics calculation speed."""
    # Pass scalar for max/min compatibility in benchmark
    val = 0.5
    
    start = time.perf_counter()
    for _ in range(1000):
        calculate_energy(val)
        calculate_entropy(np.random.rand(1000))
        calculate_roughness(np.random.rand(1000))
    end = time.perf_counter()
    
    avg_latency = (end - start) / 3000
    print(f"\n[Performance] Avg Physics Latency: {avg_latency*1e6:.2f}us")
    assert avg_latency < 0.001 # Should be under 1ms per calculation

def test_inference_cycle_performance(agent):
    """Benchmark a full active inference loop."""
    signal = np.random.rand(13)
    
    start = time.perf_counter()
    count = 100
    for _ in range(count):
        agent.minimize_surprise(signal)
    end = time.perf_counter()
    
    avg_latency = (end - start) / count
    print(f"\n[Performance] Avg Inference Cycle: {avg_latency*1e3:.2f}ms")
    assert avg_latency < 0.1 # Should be under 100ms per agent cycle

def test_holographic_retrieval_scalability(memory):
    """Benchmark memory retrieval speed at capacity."""
    vector_size = 24
    num_patterns = 100
    patterns = [np.random.randn(vector_size) for _ in range(num_patterns)]
    
    # Store
    for p in patterns:
        memory.encode(p, context=np.random.randn(vector_size))
    
    # Benchmark Retrieval
    query = patterns[0]
    start = time.perf_counter()
    for _ in range(100):
        memory.recall(query)
    end = time.perf_counter()
    
    avg_latency = (end - start) / 100
    print(f"\n[Performance] Avg Memory Retrieval: {avg_latency*1e6:.2f}us")
    assert avg_latency < 0.01 # Should be under 10ms

def test_thermodynamic_update_throughput():
    """Benchmark stress testing for thermodynamic updates."""
    system = ThermodynamicSystem()
    
    start = time.perf_counter()
    count = 10000
    for i in range(count):
        system.add_heat(0.001)
    end = time.perf_counter()
    
    avg_latency = (end - start) / count
    print(f"\n[Performance] Avg Thermo Update: {avg_latency*1e6:.2f}us")
    assert avg_latency < 0.0001 # Should be extremely fast
