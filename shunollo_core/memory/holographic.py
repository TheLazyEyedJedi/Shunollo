"""
Holographic Associative Memory
------------------------------
Distributed memory using FFT-based convolution/correlation for
content-addressable pattern storage and retrieval.

Mathematical Foundation:
    Encoding (Convolution): M_new = M_old + F⁻¹{F{v} · F{k}}
    Recall (Correlation): v_rec = F⁻¹{F{M} · F{k'}*}
    Capacity bound: C ≈ √N (space-bandwidth product limit)

Capacity is O(√N) orthogonal memories before interference dominates.
For size=1024, expect ~32 reliable memories.

References:
    Plate (2003). Holographic Reduced Representations.
    Hopfield (1982). Neural networks and physical systems.

Note:
    This module is NOT thread-safe. For concurrent access, use external
    synchronization or instantiate separate memories per thread.
"""
import numpy as np
from typing import Tuple, Optional, List, Dict
import warnings
import threading

__all__ = [
    'HolographicMemory',
    'DistributedHolographicShard',
    'create_holographic_memory',
    'shard_memory',
]


class HolographicMemory:
    """
    Associative memory using holographic (Fourier) encoding.
    
    Each memory is superimposed onto the existing pattern via circular
    convolution. Retrieval uses correlation with the query pattern.
    
    Properties:
        - Content-addressable: Query by partial pattern
        - Graceful degradation: Partial damage reduces quality
        - Interference: Too many memories cause crosstalk
    
    Attributes:
        size: Hologram size (frequency bins)
        capacity: Theoretical capacity (√size)
        memory_count: Number of stored memories
        decay_rate: Forgetting rate per encode
    """
    
    __slots__ = (
        'size', 'decay_rate', 'require_context', 'M',
        'memory_count', '_total_energy', 'capacity',
        '_capacity_warned', '_lock'
    )
    
    def __init__(
        self, 
        size: int = 1024, 
        decay_rate: float = 0.0,
        require_context: bool = True
    ) -> None:
        """
        Initialize the memory.
        
        Args:
            size: Size of holographic storage (frequency bins)
            decay_rate: Forgetting rate per encode [0, 1)
            require_context: Require distinct context keys
            
        Raises:
            ValueError: If size not positive or decay_rate out of range
        """
        if size <= 0:
            raise ValueError(f"size must be positive, got {size}")
        if decay_rate < 0 or decay_rate >= 1:
            raise ValueError(f"decay_rate must be in [0, 1), got {decay_rate}")
        
        self.size = size
        self.decay_rate = decay_rate
        self.require_context = require_context
        self.M = np.zeros(size, dtype=complex)
        self.memory_count = 0
        self._total_energy = 0.0
        self.capacity = int(np.sqrt(size))
        self._capacity_warned = False
        self._lock = threading.Lock()
    
    def __repr__(self) -> str:
        return (
            f"HolographicMemory(size={self.size}, "
            f"memory_count={self.memory_count}, "
            f"capacity={self.capacity})"
        )
    
    def _pad_to_size(self, arr: np.ndarray) -> np.ndarray:
        """Zero-pad or truncate array to hologram size."""
        arr = np.asarray(arr, dtype=float)
        if len(arr) >= self.size:
            return arr[:self.size]
        return np.pad(arr, (0, self.size - len(arr)))
    
    def encode(
        self, 
        vector: np.ndarray, 
        context: Optional[np.ndarray] = None
    ) -> None:
        """
        Store a memory vector associated with a context key.
        
        Uses circular convolution: M_new = M_old + F⁻¹{F{v} · F{k}}
        
        Args:
            vector: The memory to store (v)
            context: The retrieval key (k)
            
        Raises:
            ValueError: If context required but not provided
        """
        if self.require_context and context is None:
            raise ValueError(
                "Context key required. Provide context or set require_context=False."
            )
        
        with self._lock:
            if self.memory_count >= self.capacity and not self._capacity_warned:
                warnings.warn(
                    f"Memory count ({self.memory_count}) >= capacity ({self.capacity}). "
                    f"Retrieval accuracy will degrade.",
                    UserWarning
                )
                self._capacity_warned = True
            
            if self.decay_rate > 0:
                self.M *= (1 - self.decay_rate)
                self._total_energy *= (1 - self.decay_rate) ** 2
            
            v = self._pad_to_size(vector)
            k = self._pad_to_size(context) if context is not None else v.copy()
            
            V = np.fft.fft(v)
            K = np.fft.fft(k)
            convolution = np.fft.ifft(V * K)
            
            self.M += convolution
            self._total_energy += np.sum(np.abs(convolution) ** 2)
            self.memory_count += 1
    
    def recall(self, cue: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Retrieve memory associated with a cue.
        
        Uses correlation: v_rec = F⁻¹{F{M} · F{k'}*}
        
        Args:
            cue: The retrieval cue (k')
        
        Returns:
            Tuple of (recalled_pattern, match_strength)
        """
        with self._lock:
            k_prime = self._pad_to_size(cue)
            
            M_fft = np.fft.fft(self.M)
            K_prime_fft = np.fft.fft(k_prime)
            correlation = np.fft.ifft(M_fft * np.conj(K_prime_fft))
            
            recalled = np.real(correlation)
            
            if self._total_energy > 0:
                match_strength = np.max(np.abs(recalled)) / np.sqrt(self._total_energy)
            else:
                match_strength = 0.0
        
        return recalled, match_strength
    
    def check_resonance(
        self, 
        query: np.ndarray, 
        threshold: float = 0.1
    ) -> bool:
        """Check if query resonates with stored memories."""
        _, strength = self.recall(query)
        return strength > threshold
    
    def get_novelty(self, query: np.ndarray) -> float:
        """Get novelty score (low = familiar, high = novel)."""
        _, strength = self.recall(query)
        return 1.0 / (strength + 0.01)
    
    def get_statistics(self) -> Dict:
        """Get storage statistics."""
        with self._lock:
            utilization = self.memory_count / self.capacity if self.capacity > 0 else 0
            return {
                "memory_count": self.memory_count,
                "capacity": self.capacity,
                "utilization": utilization,
                "utilization_warning": utilization > 0.8,
                "hologram_size": self.size,
                "total_bytes": self.M.nbytes,
                "bytes_per_memory": self.M.nbytes / max(1, self.memory_count),
                "total_energy": self._total_energy
            }
    
    def get_interference_estimate(self) -> float:
        """Estimate current interference level [0, 1]."""
        if self.capacity == 0:
            return 1.0
        ratio = self.memory_count / self.capacity
        return min(1.0, ratio ** 2)
    
    def clear(self) -> None:
        """Clear all memories."""
        with self._lock:
            self.M = np.zeros(self.size, dtype=complex)
            self.memory_count = 0
            self._total_energy = 0.0
            self._capacity_warned = False
    
    def save(self, path: str) -> None:
        """Save hologram to file using numpy format."""
        with self._lock:
            np.savez_compressed(
                path,
                hologram_real=np.real(self.M),
                hologram_imag=np.imag(self.M),
                size=np.array([self.size]),
                count=np.array([self.memory_count]),
                energy=np.array([self._total_energy]),
                decay_rate=np.array([self.decay_rate])
            )
    
    def load(self, path: str) -> None:
        """
        Load hologram from file.
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        if not path.endswith('.npz'):
            path += '.npz'
        
        try:
            data = np.load(path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Hologram file not found: {path}")
        
        try:
            with self._lock:
                real = data['hologram_real']
                imag = data['hologram_imag']
                self.M = real + 1j * imag
                self.size = int(data['size'][0])
                self.memory_count = int(data['count'][0])
                self._total_energy = float(data['energy'][0])
                self.decay_rate = float(data['decay_rate'][0])
                self.capacity = int(np.sqrt(self.size))
                self._capacity_warned = self.memory_count >= self.capacity
        except KeyError as e:
            raise ValueError(f"Invalid hologram file format: missing {e}")


class DistributedHolographicShard:
    """
    A shard of a distributed holographic memory.
    
    Implements frequency-domain partitioning for distributed storage.
    Losing a shard causes notch-filter-like degradation.
    
    Attributes:
        shard_id: This shard's ID
        total_shards: Total number of shards
        shard_size: Size of this shard
    """
    
    __slots__ = (
        'shard_id', 'total_shards', 'shard', 'shard_size',
        'memory_count', '_total_energy'
    )
    
    def __init__(
        self,
        full_hologram: HolographicMemory,
        shard_id: int,
        total_shards: int
    ) -> None:
        """
        Create a shard from a full hologram.
        
        Args:
            full_hologram: The complete holographic memory
            shard_id: This shard's ID [0, total_shards)
            total_shards: Total number of shards
            
        Raises:
            ValueError: If shard_id out of range
        """
        if shard_id < 0 or shard_id >= total_shards:
            raise ValueError(
                f"shard_id must be in [0, {total_shards-1}], got {shard_id}"
            )
        
        self.shard_id = shard_id
        self.total_shards = total_shards
        
        shard_size = full_hologram.size // total_shards
        start = shard_id * shard_size
        end = start + shard_size
        
        self.shard = full_hologram.M[start:end].copy()
        self.shard_size = shard_size
        self.memory_count = full_hologram.memory_count
        self._total_energy = full_hologram._total_energy / total_shards
    
    def __repr__(self) -> str:
        return (
            f"DistributedHolographicShard(id={self.shard_id}, "
            f"total={self.total_shards}, size={self.shard_size})"
        )
    
    def partial_recall(self, cue: np.ndarray) -> Tuple[np.ndarray, float]:
        """Recall from partial shard with reduced quality."""
        cue_padded = np.zeros(self.shard_size, dtype=float)
        cue_len = min(len(cue), self.shard_size)
        cue_padded[:cue_len] = np.asarray(cue[:cue_len], dtype=float)
        
        shard_fft = np.fft.fft(self.shard)
        cue_fft = np.fft.fft(cue_padded)
        correlation = np.fft.ifft(shard_fft * np.conj(cue_fft))
        
        recalled = np.real(correlation)
        
        if self._total_energy > 0:
            strength = np.max(np.abs(recalled)) / np.sqrt(self._total_energy)
        else:
            strength = 0.0
        
        return recalled, strength
    
    @classmethod
    def reconstruct_from_shards(
        cls,
        shards: List['DistributedHolographicShard'],
        original_size: int
    ) -> HolographicMemory:
        """
        Reconstruct hologram from available shards.
        
        Missing shards result in frequency gaps (notch filtering).
        
        Args:
            shards: Available shards (may be incomplete)
            original_size: Size of the original hologram
        
        Returns:
            Reconstructed HolographicMemory
        """
        if not shards:
            return HolographicMemory(size=original_size, require_context=False)
        
        reconstructed = HolographicMemory(size=original_size, require_context=False)
        
        for shard in shards:
            start = shard.shard_id * shard.shard_size
            end = start + shard.shard_size
            reconstructed.M[start:end] = shard.shard
        
        present_ids = {s.shard_id for s in shards}
        total_shards = shards[0].total_shards
        missing_shards = set(range(total_shards)) - present_ids
        
        if missing_shards:
            warnings.warn(
                f"Missing shards {missing_shards}: reconstruction has frequency gaps"
            )
        
        reconstructed.memory_count = shards[0].memory_count
        reconstructed._total_energy = sum(s._total_energy for s in shards)
        
        return reconstructed


def create_holographic_memory(
    size: int = 1024,
    decay_rate: float = 0.0,
    require_context: bool = True
) -> HolographicMemory:
    """Create a HolographicMemory instance."""
    return HolographicMemory(
        size=size,
        decay_rate=decay_rate,
        require_context=require_context
    )


def shard_memory(
    memory: HolographicMemory,
    n_shards: int
) -> List[DistributedHolographicShard]:
    """Split a holographic memory into distributed shards."""
    if n_shards <= 0:
        raise ValueError(f"n_shards must be positive, got {n_shards}")
    if n_shards > memory.size:
        raise ValueError(f"n_shards ({n_shards}) > memory size ({memory.size})")
    
    return [
        DistributedHolographicShard(memory, i, n_shards)
        for i in range(n_shards)
    ]
