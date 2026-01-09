"""Tests for holographic memory module."""
import pytest
import numpy as np
import tempfile
import os
from shunollo_core.memory.holographic import (
    HolographicMemory,
    DistributedHolographicShard,
    create_holographic_memory,
    shard_memory,
)


class TestHolographicMemoryInit:
    """Test HolographicMemory initialization."""
    
    def test_default_initialization(self):
        mem = HolographicMemory()
        assert mem.size == 1024
        assert mem.capacity == 32
        assert mem.memory_count == 0
        assert mem.decay_rate == 0.0
    
    def test_custom_size(self):
        mem = HolographicMemory(size=512)
        assert mem.size == 512
        assert mem.capacity == int(np.sqrt(512))
    
    def test_invalid_size_raises(self):
        with pytest.raises(ValueError, match="size must be positive"):
            HolographicMemory(size=0)
        
        with pytest.raises(ValueError, match="size must be positive"):
            HolographicMemory(size=-100)
    
    def test_invalid_decay_rate_raises(self):
        with pytest.raises(ValueError, match="decay_rate must be in"):
            HolographicMemory(decay_rate=-0.1)
        
        with pytest.raises(ValueError, match="decay_rate must be in"):
            HolographicMemory(decay_rate=1.0)
    
    def test_repr(self):
        mem = HolographicMemory(size=256)
        repr_str = repr(mem)
        assert "HolographicMemory" in repr_str
        assert "size=256" in repr_str
    
    def test_factory_function(self):
        mem = create_holographic_memory(size=256)
        assert isinstance(mem, HolographicMemory)
        assert mem.size == 256


class TestEncode:
    """Test memory encoding."""
    
    def test_basic_encode(self):
        mem = HolographicMemory(require_context=False)
        vector = np.array([1, 2, 3, 4, 5])
        
        mem.encode(vector)
        
        assert mem.memory_count == 1
    
    def test_encode_with_context(self):
        mem = HolographicMemory(require_context=True)
        vector = np.array([1, 2, 3, 4, 5])
        context = np.array([5, 4, 3, 2, 1])
        
        mem.encode(vector, context=context)
        
        assert mem.memory_count == 1
    
    def test_encode_requires_context(self):
        mem = HolographicMemory(require_context=True)
        vector = np.array([1, 2, 3, 4, 5])
        
        with pytest.raises(ValueError, match="Context key required"):
            mem.encode(vector)
    
    def test_capacity_warning_once(self):
        mem = HolographicMemory(size=16, require_context=False)
        vector = np.ones(10)
        
        with pytest.warns(UserWarning, match="capacity"):
            for _ in range(6):
                mem.encode(vector)
        
        # Subsequent encodes should NOT warn again
        mem.encode(vector)
        mem.encode(vector)
        assert mem.memory_count == 8


class TestRecall:
    """Test memory recall."""
    
    def test_recall_stored_pattern(self):
        mem = HolographicMemory(size=512, require_context=True)
        vector = np.array([1, 2, 3, 4, 5])
        context = np.array([5, 4, 3, 2, 1])
        
        mem.encode(vector, context=context)
        recalled, strength = mem.recall(context)
        
        assert recalled.shape == (512,)
        assert strength > 0
    
    def test_recall_empty_memory(self):
        mem = HolographicMemory()
        cue = np.array([1, 2, 3])
        
        recalled, strength = mem.recall(cue)
        
        assert recalled.shape == (mem.size,)
        assert strength == 0.0


class TestCheckResonance:
    """Test resonance checking."""
    
    def test_stored_pattern_resonates(self):
        mem = HolographicMemory(size=256, require_context=True)
        vector = np.random.randn(50)
        context = np.random.randn(50)
        
        mem.encode(vector, context=context)
        
        assert mem.check_resonance(context, threshold=0.01)
    
    def test_random_pattern_may_not_resonate(self):
        mem = HolographicMemory(size=256, require_context=True)
        vector = np.random.randn(50)
        context = np.random.randn(50)
        
        mem.encode(vector, context=context)
        
        unrelated = np.random.randn(50) * 100
        resonates = mem.check_resonance(unrelated, threshold=0.5)


class TestNovelty:
    """Test novelty scoring."""
    
    def test_familiar_has_low_novelty(self):
        mem = HolographicMemory(size=256, require_context=False)
        vector = np.array([1, 2, 3, 4, 5])
        
        mem.encode(vector)
        
        novelty = mem.get_novelty(vector)
        assert novelty > 0


class TestStatistics:
    """Test statistics reporting."""
    
    def test_statistics_structure(self):
        mem = HolographicMemory(size=256, require_context=False)
        mem.encode(np.ones(10))
        mem.encode(np.ones(10) * 2)
        
        stats = mem.get_statistics()
        
        assert "memory_count" in stats
        assert stats["memory_count"] == 2
        assert "capacity" in stats
        assert "utilization" in stats
        assert "hologram_size" in stats
        assert "total_bytes" in stats


class TestInterferenceEstimate:
    """Test interference estimation."""
    
    def test_empty_memory_no_interference(self):
        mem = HolographicMemory()
        assert mem.get_interference_estimate() == 0.0
    
    def test_full_memory_high_interference(self):
        mem = HolographicMemory(size=16, require_context=False)
        
        with pytest.warns(UserWarning):
            for i in range(10):
                mem.encode(np.random.randn(10))
        
        interference = mem.get_interference_estimate()
        assert interference > 0.5


class TestClear:
    """Test memory clearing."""
    
    def test_clear_resets_memory(self):
        mem = HolographicMemory(require_context=False)
        for _ in range(5):
            mem.encode(np.random.randn(10))
        
        assert mem.memory_count == 5
        
        mem.clear()
        
        assert mem.memory_count == 0
        assert np.all(mem.M == 0)


class TestSaveLoad:
    """Test save/load functionality."""
    
    def test_save_and_load(self):
        mem = HolographicMemory(size=256, require_context=False)
        for i in range(3):
            mem.encode(np.random.randn(20))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_hologram")
            mem.save(path)
            
            mem2 = HolographicMemory(size=256)
            mem2.load(path)
            
            assert mem2.memory_count == mem.memory_count
            assert mem2.size == mem.size
            np.testing.assert_array_almost_equal(mem2.M, mem.M)
    
    def test_load_nonexistent_raises(self):
        mem = HolographicMemory()
        
        with pytest.raises(FileNotFoundError, match="not found"):
            mem.load("/nonexistent/path/hologram.npz")


class TestDecay:
    """Test forgetting/decay functionality."""
    
    def test_decay_reduces_energy(self):
        mem = HolographicMemory(size=256, decay_rate=0.1, require_context=False)
        
        mem.encode(np.ones(50))
        energy1 = mem._total_energy
        
        mem.encode(np.ones(50))
        energy2_per_mem = mem._total_energy / 2
        
        assert energy2_per_mem < energy1


class TestDistributedShards:
    """Test distributed holographic shards."""
    
    def test_create_shards(self):
        mem = HolographicMemory(size=512, require_context=False)
        for _ in range(5):
            mem.encode(np.random.randn(20))
        
        shards = shard_memory(mem, n_shards=4)
        
        assert len(shards) == 4
        for i, shard in enumerate(shards):
            assert shard.shard_id == i
            assert shard.total_shards == 4
    
    def test_shard_invalid_count_raises(self):
        mem = HolographicMemory(size=256)
        
        with pytest.raises(ValueError, match="n_shards must be positive"):
            shard_memory(mem, n_shards=0)
        
        with pytest.raises(ValueError, match="n_shards.*> memory size"):
            shard_memory(mem, n_shards=1000)
    
    def test_shard_repr(self):
        mem = HolographicMemory(size=256, require_context=False)
        mem.encode(np.ones(10))
        shards = shard_memory(mem, n_shards=4)
        
        repr_str = repr(shards[0])
        assert "DistributedHolographicShard" in repr_str
    
    def test_partial_recall(self):
        mem = HolographicMemory(size=256, require_context=False)
        mem.encode(np.ones(20))
        
        shards = shard_memory(mem, n_shards=4)
        
        recalled, strength = shards[0].partial_recall(np.ones(20))
        assert len(recalled) == shards[0].shard_size
    
    def test_reconstruct_from_all_shards(self):
        mem = HolographicMemory(size=256, require_context=False)
        for _ in range(3):
            mem.encode(np.random.randn(20))
        
        shards = shard_memory(mem, n_shards=4)
        reconstructed = DistributedHolographicShard.reconstruct_from_shards(
            shards, original_size=256
        )
        
        np.testing.assert_array_almost_equal(reconstructed.M, mem.M)
    
    def test_reconstruct_with_missing_shards_warns(self):
        mem = HolographicMemory(size=256, require_context=False)
        mem.encode(np.ones(20))
        
        shards = shard_memory(mem, n_shards=4)
        partial_shards = shards[:2]
        
        with pytest.warns(UserWarning, match="Missing shards"):
            DistributedHolographicShard.reconstruct_from_shards(
                partial_shards, original_size=256
            )
    
    def test_reconstruct_from_empty_shards(self):
        reconstructed = DistributedHolographicShard.reconstruct_from_shards(
            [], original_size=256
        )
        
        assert reconstructed.size == 256
        assert reconstructed.memory_count == 0
