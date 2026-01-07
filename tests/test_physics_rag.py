"""
test_physics_rag.py - Unit Tests for Physics-RAG (The Recall Loop)

Tests the core episodic memory recall capabilities:
- to_vector(): 18-dimensional normalized physics fingerprint export
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
        """Vector should always be 18 dimensions."""
        signal = ShunolloSignal()
        vector = signal.to_vector()
        assert len(vector) == 18, f"Expected 18 dimensions, got {len(vector)}"
    
    def test_vector_values_match_fields(self):
        """Vector values should be normalized to 0-1 range."""
        signal = ShunolloSignal(
            energy=5.0,      # 0-10 range -> 0.5 normalized
            entropy=4.0,     # 0-8 range -> 0.5 normalized
            roughness=0.5,   # 0-1 range -> 0.5 normalized
        )
        vector = signal.to_vector(normalize=True)
        assert len(vector) == 18
        # Energy (index 0): 5.0 in 0-10 range = 0.5
        assert abs(vector[0] - 0.5) < 0.01, f"Energy normalization failed: {vector[0]}"
        # Entropy (index 1): 4.0 in 0-8 range = 0.5
        assert abs(vector[1] - 0.5) < 0.01, f"Entropy normalization failed: {vector[1]}"
        # Roughness (index 3): 0.5 in 0-1 range = 0.5
        assert abs(vector[3] - 0.5) < 0.01, f"Roughness normalization failed: {vector[3]}"
    
    def test_vector_unnormalized(self):
        """Unnormalized vector should return raw values."""
        signal = ShunolloSignal(energy=5.0, entropy=4.0)
        vector = signal.to_vector(normalize=False)
        assert vector[0] == 5.0, "Raw energy should be 5.0"
        assert vector[1] == 4.0, "Raw entropy should be 4.0"
    
    def test_default_signal_zero_vector_unnormalized(self):
        """Default signal unnormalized should produce all-zeros."""
        signal = ShunolloSignal()
        vector = signal.to_vector(normalize=False)
        assert all(v == 0.0 for v in vector), "Raw default signal should have zero vector"
    
    def test_normalized_vector_range(self):
        """All normalized values should be in [0, 1] range."""
        signal = ShunolloSignal(
            energy=5.0, entropy=4.0, frequency=500.0, 
            roughness=0.5, pan=-0.5, spatial_x=0.5
        )
        vector = signal.to_vector(normalize=True)
        for i, v in enumerate(vector):
            assert 0.0 <= v <= 1.0, f"Normalized value at index {i} out of range: {v}"


class TestRecallSimilar:
    """Tests for Hippocampus.recall_similar()"""
    
    @pytest.fixture
    def temp_hippocampus(self):
        """Create a hippocampus with temporary storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Properly create hippocampus without calling config-dependent __init__
            with patch.object(Hippocampus, '__init__', lambda self, **kwargs: None):
                hippo = Hippocampus.__new__(Hippocampus)
                hippo.storage_path = Path(tmpdir) / "episodic_memory.jsonl"
                hippo._cache = None
                hippo._cache_dirty = True
                hippo._max_cache_size = 10000
                yield hippo
    
    def test_recall_empty_memory(self, temp_hippocampus):
        """Recall on empty memory should return empty list."""
        query = [0.0] * 18
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
        
        # Query with slightly different vector (stored signal normalized)
        stored_vector = signal.to_vector(normalize=True)
        # Slightly offset the query
        query = [v + 0.1 if i < 3 else v for i, v in enumerate(stored_vector)]
        result = temp_hippocampus.recall_similar(query, threshold=1.0)
        
        assert len(result) == 1, "Should find 1 similar signal"
        _, distance = result[0]
        assert distance < 1.0, "Distance should be within threshold"
    
    def test_recall_respects_threshold(self, temp_hippocampus):
        """Signals outside threshold should not be returned."""
        # Store a signal
        signal = ShunolloSignal(energy=1.0)
        temp_hippocampus.remember(signal)
        
        # Query with very different vector (far from stored)
        query = [1.0] * 18  # All maxed out in normalized space
        result = temp_hippocampus.recall_similar(query, threshold=0.1)  # Very tight threshold
        
        assert result == [], "Far signal should not match with tight threshold"
    
    def test_recall_returns_top_k(self, temp_hippocampus):
        """Should return at most k results."""
        # Store 5 signals
        for i in range(5):
            signal = ShunolloSignal(energy=float(i))
            temp_hippocampus.remember(signal)
        
        # Query for top 3
        query = [0.0] * 18
        result = temp_hippocampus.recall_similar(query, k=3, threshold=10.0)
        
        assert len(result) <= 3, f"Should return at most 3 results, got {len(result)}"
    
    def test_recall_sorted_by_distance(self, temp_hippocampus):
        """Results should be sorted by distance (closest first)."""
        # Store signals at different distances
        temp_hippocampus.remember(ShunolloSignal(energy=5.0))  # Far
        temp_hippocampus.remember(ShunolloSignal(energy=1.0))  # Close
        temp_hippocampus.remember(ShunolloSignal(energy=3.0))  # Medium
        
        # Query from origin
        query = [0.0] * 18
        result = temp_hippocampus.recall_similar(query, k=3, threshold=10.0)
        
        distances = [d for _, d in result]
        assert distances == sorted(distances), "Results should be sorted by distance"
    
    def test_novelty_score(self, temp_hippocampus):
        """Test get_novelty_score returns distance to nearest neighbor."""
        # Store a signal
        signal = ShunolloSignal(energy=5.0, roughness=0.5)
        temp_hippocampus.remember(signal)
        
        # Same signal should have novelty 0
        assert temp_hippocampus.get_novelty_score(signal.to_vector()) == 0.0
        
        # Empty memory should return infinity
        temp_hippocampus.clear_memory()
        query = [0.5] * 18
        assert temp_hippocampus.get_novelty_score(query) == float('inf')
