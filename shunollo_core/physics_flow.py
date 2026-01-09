"""
Flow Topology Analysis
----------------------
Detects geometric inefficiencies in data flow topology using resistance
and imbalance metrics inspired by fluid dynamics and thermodynamics.

Mathematical Foundation:
    Configurational Resistance: R_c = ΔP / Φ (Ohm's Law for fluids)
    Flow Imbalance: I = |T - V| where T,V are dimensionless normalized metrics

All inputs are normalized to dimensionless ratios before computation to
ensure physical consistency.

Note:
    This module is NOT thread-safe. For concurrent access, use external
    synchronization or instantiate separate analyzers per thread.
"""
import numpy as np
from typing import Tuple, Optional
from collections import deque
import threading

__all__ = [
    'VascularAnalyzer',
    'get_vascular_analyzer',
    'MIN_CPU_LOAD',
    'MIN_THROUGHPUT',
    'TURBULENCE_THRESHOLD',
]

MIN_CPU_LOAD = 0.01
MIN_THROUGHPUT = 1.0
TURBULENCE_THRESHOLD = 0.5


class VascularAnalyzer:
    """
    Measures configurational resistance and flow imbalance in data topologies.
    
    Analogous to monitoring vascular resistance in circulatory systems.
    This module only measures - for active regulation, pair with an
    ActiveInferenceAgent.
    
    Attributes:
        window_size: Number of samples for imbalance integration
        baseline_bytes: Reference throughput for normalization [bytes]
        baseline_latency: Reference latency for normalization [ms]
    """
    
    __slots__ = (
        'window_size', 'baseline_bytes', 'baseline_latency',
        '_history', '_resistance_history', '_lock'
    )
    
    def __init__(
        self, 
        window_size: int = 100,
        baseline_bytes: float = 1000.0,
        baseline_latency: float = 100.0
    ) -> None:
        """
        Initialize the analyzer.
        
        Args:
            window_size: Number of samples for imbalance integration (τ)
            baseline_bytes: Reference throughput for normalization [bytes]
            baseline_latency: Reference latency for normalization [ms]
            
        Raises:
            ValueError: If window_size is not positive
        """
        if window_size <= 0:
            raise ValueError(f"window_size must be positive, got {window_size}")
        
        self.window_size = window_size
        self.baseline_bytes = baseline_bytes
        self.baseline_latency = baseline_latency
        self._history: deque = deque(maxlen=window_size)
        self._resistance_history: deque = deque(maxlen=10)
        self._lock = threading.Lock()
    
    def __repr__(self) -> str:
        return (
            f"VascularAnalyzer(window_size={self.window_size}, "
            f"baseline_bytes={self.baseline_bytes}, "
            f"baseline_latency={self.baseline_latency})"
        )
    
    def calculate_configurational_resistance(
        self, 
        queue_depth: float,
        cpu_load: float,
        throughput_bps: float
    ) -> float:
        """
        Calculate configurational resistance R_c = ΔP / Φ.
        
        Args:
            queue_depth: Number of items in processing queue [items]
            cpu_load: CPU utilization ratio [0.0 - 1.0]
            throughput_bps: Throughput [bits/second]
        
        Returns:
            Configurational resistance [dimensionless, normalized]
        
        Raises:
            ValueError: If inputs are out of valid range
        """
        if queue_depth < 0:
            raise ValueError(
                f"queue_depth cannot be negative (got {queue_depth}), "
                "indicates counter rollover or measurement error"
            )
        if cpu_load < 0 or cpu_load > 1.0:
            raise ValueError(f"cpu_load must be in [0, 1], got {cpu_load}")
        if throughput_bps < 0:
            raise ValueError(f"throughput_bps cannot be negative (got {throughput_bps})")
        
        if throughput_bps < MIN_THROUGHPUT:
            return float('inf')
        
        delta_p = queue_depth * max(cpu_load, MIN_CPU_LOAD)
        r_c = delta_p / throughput_bps
        
        with self._lock:
            self._resistance_history.append(r_c)
        
        return r_c
    
    def calculate_flow_imbalance(
        self,
        bytes_out: float,
        latency_ms: float
    ) -> float:
        """
        Calculate flow imbalance I = |T_normalized - V_normalized|.
        
        Both metrics are normalized to dimensionless ratios before computing
        imbalance. In an efficient system at equilibrium: T ≈ V.
        
        Args:
            bytes_out: Bytes transmitted [bytes]
            latency_ms: Response latency [milliseconds]
        
        Returns:
            Instantaneous flow imbalance [dimensionless, 0 = equilibrium]
        
        Raises:
            ValueError: If inputs are negative
        """
        if bytes_out < 0:
            raise ValueError(f"bytes_out cannot be negative (got {bytes_out})")
        if latency_ms < 0:
            raise ValueError(f"latency_ms cannot be negative (got {latency_ms})")
        
        normalized_throughput = bytes_out / self.baseline_bytes
        normalized_latency = latency_ms / self.baseline_latency
        
        t_kinetic = np.log1p(normalized_throughput)
        v_potential = np.log1p(normalized_latency)
        
        imbalance = abs(t_kinetic - v_potential)
        
        with self._lock:
            self._history.append(imbalance)
        
        return imbalance
    
    def get_integrated_imbalance(self) -> float:
        """
        Get accumulated imbalance over observation window.
        
        Returns:
            Integrated imbalance [dimensionless]
        """
        with self._lock:
            if not self._history:
                return 0.0
            return float(sum(self._history))
    
    def get_mean_imbalance(self) -> float:
        """
        Get average imbalance over the observation window.
        
        Returns:
            Mean imbalance [dimensionless, 0 = perfect equilibrium]
        """
        with self._lock:
            if not self._history:
                return 0.0
            return sum(self._history) / len(self._history)
    
    def detect_topology_anomaly(
        self,
        sources: int,
        sinks: int,
        edges: int
    ) -> Tuple[bool, float]:
        """
        Detect non-tree topology indicating potential DDoS or amplification.
        
        For a spanning tree: edges = nodes - 1
        # For mesh/surge: edges >> nodes - 1
        
        Note:
            Legitimate mesh networks (load balancers, CDNs) may trigger this.
            Use domain knowledge to calibrate the threshold.
        
        Args:
            sources: Number of data sources
            sinks: Number of data sinks  
            edges: Number of connections
        
        Returns:
            Tuple of (is_anomalous, turbulence_score in [0, 1])
        """
        if sources < 0 or sinks < 0 or edges < 0:
            raise ValueError("Graph parameters cannot be negative")
        
        node_count = sources + sinks
        if node_count <= 1:
            return False, 0.0
        
        tree_edges = node_count - 1
        turbulence = (edges - tree_edges) / tree_edges
        turbulence_score = min(1.0, max(0.0, turbulence))
        is_anomalous = turbulence > TURBULENCE_THRESHOLD
        
        return is_anomalous, turbulence_score
    
    def check_resistance_trend(self) -> Tuple[bool, float]:
        """
        Check if resistance is increasing over time.
        
        Persistent systems should evolve toward lower resistance.
        Increasing resistance suggests system degradation.
        
        Returns:
            Tuple of (is_increasing, trend_slope)
        """
        with self._lock:
            if len(self._resistance_history) < 2:
                return False, 0.0
            
            recent = list(self._resistance_history)
        
        n = len(recent)
        x = np.arange(n)
        slope = np.polyfit(x, recent, 1)[0]
        
        return slope > 0, float(slope)
    
    def reset(self) -> None:
        """Clear all history."""
        with self._lock:
            self._history.clear()
            self._resistance_history.clear()
    
    def update_baselines(
        self, 
        bytes_baseline: float, 
        latency_baseline: float
    ) -> None:
        """
        Update normalization baselines.
        
        Args:
            bytes_baseline: New reference throughput [bytes]
            latency_baseline: New reference latency [ms]
            
        Raises:
            ValueError: If baselines are not positive
        """
        if bytes_baseline <= 0 or latency_baseline <= 0:
            raise ValueError("Baselines must be positive")
        self.baseline_bytes = bytes_baseline
        self.baseline_latency = latency_baseline


def get_vascular_analyzer(
    window_size: int = 100,
    baseline_bytes: float = 1000.0,
    baseline_latency: float = 100.0
) -> VascularAnalyzer:
    """Create a VascularAnalyzer instance."""
    return VascularAnalyzer(
        window_size=window_size,
        baseline_bytes=baseline_bytes,
        baseline_latency=baseline_latency
    )
