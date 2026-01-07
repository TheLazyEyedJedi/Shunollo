"""
test_physics_rag.py - Unit Tests for Physics-RAG (The Recall Loop)

Tests the core episodic memory recall capabilities:
- to_vector(): 13-dimensional physics fingerprint export
- recall_similar(): Euclidean distance-based similarity search
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

from shunollo_core.models import ShunolloSignal
from shunollo_core.memory.hippocampus import Hippocampus


class TestToVector:
    """Tests for ShunolloSignal.to_vector()"""
    
    def test_vector_dimensionality(self):
        """Vector should always be 13 dimensions."""
        signal = ShunolloSignal()
        vector = signal.to_vector()
        assert len(vector) == 13, f"Expected 13 dimensions, got {len(vector)}"
    
    def test_vector_values_match_fields(self):
        """Vector values should match the physics fields in correct order."""
        signal = ShunolloSignal(
            energy=1.0,
            entropy=2.0,
            frequency=3.0,
            roughness=4.0,
            viscosity=5.0,
            volatility=6.0,
            action=7.0,
            hamiltonian=8.0,
            ewr=9.0,
            harmony=10.0,
            flux=11.0,
            dissonance=12.0,
            hue=13.0,
        )
        vector = signal.to_vector()
        expected = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0]
        assert vector == expected, f"Vector mismatch: {vector} != {expected}"
    
    def test_default_signal_zero_vector(self):
        """Default signal should produce all-zeros except metadata doesn't affect vector."""
        signal = ShunolloSignal()
        vector = signal.to_vector()
        assert all(v == 0.0 for v in vector), "Default signal should have zero vector"


class TestRecallSimilar:
    """Tests for Hippocampus.recall_similar()"""
    
    @pytest.fixture
    def temp_hippocampus(self):
        """Create a hippocampus with temporary storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Hippocampus, '__init__', lambda self: None):
                hippo = Hippocampus.__new__(Hippocampus)
                hippo.storage_path = Path(tmpdir) / "episodic_memory.jsonl"
                yield hippo
    
    def test_recall_empty_memory(self, temp_hippocampus):
        """Recall on empty memory should return empty list."""
        query = [0.0] * 13
        result = temp_hippocampus.recall_similar(query)
        assert result == [], "Empty memory should return empty list"
    
    def test_recall_exact_match(self, temp_hippocampus):
        """Exact match should have distance 0."""
        # Store a signal
        signal = ShunolloSignal(energy=1.0, entropy=0.5, roughness=0.8)
        temp_hippocampus.remember(signal)
        
        # Query with same vector
        query = signal.to_vector()
        result = temp_hippocampus.recall_similar(query, threshold=1.0)
        
        assert len(result) == 1, "Should find exactly 1 match"
        matched_signal, distance = result[0]
        assert distance == 0.0, f"Exact match should have distance 0, got {distance}"
    
    def test_recall_similar_signals(self, temp_hippocampus):
        """Similar signals should be found within threshold."""
        # Store a signal
        signal = ShunolloSignal(energy=1.0, entropy=0.5, roughness=0.8)
        temp_hippocampus.remember(signal)
        
        # Query with slightly different vector
        query = [1.1, 0.6, 0.0, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        result = temp_hippocampus.recall_similar(query, threshold=1.0)
        
        assert len(result) == 1, "Should find 1 similar signal"
        _, distance = result[0]
        assert distance < 1.0, "Distance should be within threshold"
    
    def test_recall_respects_threshold(self, temp_hippocampus):
        """Signals outside threshold should not be returned."""
        # Store a signal
        signal = ShunolloSignal(energy=1.0)
        temp_hippocampus.remember(signal)
        
        # Query with very different vector
        query = [10.0] * 13  # Far from origin
        result = temp_hippocampus.recall_similar(query, threshold=0.5)
        
        assert result == [], "Far signal should not match with tight threshold"
    
    def test_recall_returns_top_k(self, temp_hippocampus):
        """Should return at most k results."""
        # Store 5 signals
        for i in range(5):
            signal = ShunolloSignal(energy=float(i))
            temp_hippocampus.remember(signal)
        
        # Query for top 3
        query = [0.0] * 13
        result = temp_hippocampus.recall_similar(query, k=3, threshold=10.0)
        
        assert len(result) <= 3, f"Should return at most 3 results, got {len(result)}"
    
    def test_recall_sorted_by_distance(self, temp_hippocampus):
        """Results should be sorted by distance (closest first)."""
        # Store signals at different distances
        temp_hippocampus.remember(ShunolloSignal(energy=5.0))  # Far
        temp_hippocampus.remember(ShunolloSignal(energy=1.0))  # Close
        temp_hippocampus.remember(ShunolloSignal(energy=3.0))  # Medium
        
        # Query from origin
        query = [0.0] * 13
        result = temp_hippocampus.recall_similar(query, k=3, threshold=10.0)
        
        distances = [d for _, d in result]
        assert distances == sorted(distances), "Results should be sorted by distance"
