"""
example_holographic_memory.py
-----------------------------
Using Holographic Memory for Pattern Recognition

This example shows how holographic memory enables:
1. Content-addressable recall (find by partial pattern)
2. Graceful degradation (works even with damage)
3. Novelty detection (is this new?)

Domain: Anomaly memory, incident databases, pattern matching
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from shunollo_core.memory.holographic import (
    HolographicMemory,
    shard_memory,
    DistributedHolographicShard,
)


def demonstrate_basic_memory():
    """Show basic encode/recall functionality."""
    print("=" * 60)
    print("HOLOGRAPHIC MEMORY: Content-Addressable Pattern Storage")
    print("=" * 60)
    
    memory = HolographicMemory(size=512, require_context=True)
    
    # Store some "incident patterns"
    patterns = {
        "high_flux_event": np.array([1, 0, 1, 0, 1, 0.8, 0.9, 0.7]),
        "market_crash": np.array([0, 0, 0, 0, 0, 0, 0.1, 0.2]),
        "stable_heartbeat": np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
    }
    
    # Store patterns
    contexts = {
        "high_flux_event": np.array([1, 2, 3, 4, 5, 6, 7, 8]),
        "market_crash": np.array([8, 7, 6, 5, 4, 3, 2, 1]), 
        "stable_heartbeat": np.array([1, 1, 1, 1, 1, 1, 1, 1])
    }
    
    for name, pattern in patterns.items():
        memory.encode(pattern, context=contexts[name])
        
    print("Stored 3 patterns (High Flux, Market, Heartbeat)")
    
    # 2. Recall
    print("\n[Recall] Querying with 'High Flux' context...")
    recalled, strength = memory.recall(contexts["high_flux_event"])
    print(f"  Match strength: {strength:.4f}")
    
    stats = memory.get_statistics()
    print(f"\nMemory stats:")
    print(f"  Stored: {stats['memory_count']} / {stats['capacity']} capacity")


def demonstrate_novelty_detection():
    """Show how to detect novel patterns."""
    print("\n" + "=" * 60)
    print("NOVELTY DETECTION: Is This Pattern New?")
    print("=" * 60)
    
    memory = HolographicMemory(size=256, require_context=True)
    
    # Train on known patterns
    known_patterns = [
        (np.random.randn(20), np.random.randn(20))
        for _ in range(5)
    ]
    
    print("\nTraining on 5 known incident patterns...")
    for pattern, context in known_patterns:
        memory.encode(pattern, context=context)
    
    # Test with a known pattern (should resonate)
    known_pattern, known_context = known_patterns[0]
    resonates = memory.check_resonance(known_context, threshold=0.1)
    novelty = memory.get_novelty(known_context)
    print(f"\nKnown pattern:")
    print(f"  Resonates: {resonates}")
    print(f"  Novelty score: {novelty:.2f} (low = familiar)")
    
    # Test with a novel pattern (should NOT resonate strongly)
    novel_pattern = np.random.randn(20) * 5  # Very different
    resonates = memory.check_resonance(novel_pattern, threshold=0.1)
    novelty = memory.get_novelty(novel_pattern)
    print(f"\nNovel pattern:")
    print(f"  Resonates: {resonates}")
    print(f"  Novelty score: {novelty:.2f} (high = new)")
    
    if novelty > 10:
        print("\n[!] ALERT: Never-before-seen incident pattern!")


def demonstrate_distributed_resilience():
    """Show graceful degradation with sharding."""
    print("\n" + "=" * 60)
    print("DISTRIBUTED MEMORY: Graceful Degradation")
    print("=" * 60)
    
    # Create and populate memory
    memory = HolographicMemory(size=256, require_context=False)
    
    test_patterns = [np.random.randn(30) for _ in range(10)]
    for pattern in test_patterns:
        memory.encode(pattern)
    
    print(f"\nStored {memory.memory_count} patterns")
    
    # Shard into 4 pieces (simulating distributed nodes)
    shards = shard_memory(memory, n_shards=4)
    print(f"Split into {len(shards)} shards")
    
    # Simulate losing 1 shard (node failure)
    surviving_shards = shards[:3]  # Lost shard 3
    print(f"Simulated failure: Lost shard 3")
    
    # Reconstruct from surviving shards
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        reconstructed = DistributedHolographicShard.reconstruct_from_shards(
            surviving_shards, original_size=256
        )
    
    print(f"\nReconstruction:")
    print(f"  Original memory count: {memory.memory_count}")
    print(f"  Reconstructed count: {reconstructed.memory_count}")
    
    # Test recall quality
    test_cue = test_patterns[0]
    original_recall, original_strength = memory.recall(test_cue)
    degraded_recall, degraded_strength = reconstructed.recall(test_cue)
    
    quality_ratio = degraded_strength / (original_strength + 0.001)
    print(f"\nRecall quality with 25% data loss:")
    print(f"  Original strength: {original_strength:.4f}")
    print(f"  Degraded strength: {degraded_strength:.4f}")
    print(f"  Quality retained: {quality_ratio:.1%}")
    
    print("\n[OK] Memory still functional despite node failure!")


def demonstrate_capacity_limits():
    """Show what happens at capacity."""
    print("\n" + "=" * 60)
    print("CAPACITY LIMITS: Interference Effects")
    print("=" * 60)
    
    memory = HolographicMemory(size=64, require_context=False)  # Small for demo
    
    print(f"\nMemory capacity: {memory.capacity} patterns")
    print("Storing patterns until interference occurs...\n")
    
    import warnings
    
    for i in range(memory.capacity + 5):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            memory.encode(np.random.randn(10))
            
            if w:
                print(f"  Pattern {i+1}: [!] {w[0].message}")
            else:
                interference = memory.get_interference_estimate()
                print(f"  Pattern {i+1}: stored (interference: {interference:.2f})")
    
    print(f"\nFinal interference level: {memory.get_interference_estimate():.2f}")
    print("High interference = retrieval accuracy degraded")


if __name__ == "__main__":
    demonstrate_basic_memory()
    demonstrate_novelty_detection()
    demonstrate_distributed_resilience()
    demonstrate_capacity_limits()
    print("\n[DONE] Holographic memory example complete!")
