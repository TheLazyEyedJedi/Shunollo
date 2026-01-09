"""
domain_adapter.py
-----------------
Universal Domain Adapter for Shunollo

## Two Usage Modes:

1. **BOLT-ON MODE**: Attach Shunollo to existing systems
   ```python
   adapter = UniversalAdapter("network")
   qualia = adapter.process(existing_metrics_dict)
   # Feed qualia to your existing AI/monitoring
   ```

2. **FOUNDATION MODE**: Build new applications on Shunollo
   ```python
   from shunollo_core.domain_adapter import create_adapter
   from shunollo_core.cognition.active_inference import ActiveInferenceAgent
   
   adapter = create_adapter("iot")
   agent = ActiveInferenceAgent(input_dim=10)
   
   while True:
       raw = read_sensors()
       qualia = adapter.process(raw)
       action = agent.minimize_surprise(qualia_to_vector(qualia))
   ```

## Supported Normalization Schemes:

- **unipolar** [0, 1]: Standard intensity (brightness, pressure, load)
- **bipolar** [-1, 1]: Directional data (price delta, velocity, imbalance)  
- **log**: Logarithmic scaling (decibels, magnitudes, counts)
- **unbounded**: Auto-scaling for growing values (with percentile normalization)

Any data source can be adapted:
- Physical sensors (temperature, pressure, humidity, vibration)
- Electronic signals (voltage, current, frequency)
- Digital streams (network packets, API responses, database metrics)
- Financial data (prices, volumes, order flow)
- Any time-series or event stream
"""
from typing import Dict, Any, Optional, Callable, Literal
from dataclasses import dataclass, field
import math
from shunollo_core.physics import (
    calculate_entropy,
    calculate_energy,
    calculate_roughness,
    calculate_viscosity,
    calculate_harmony,
    calculate_flux,
    calculate_dissonance,
    calculate_ewr,
    calculate_volatility_index,
    calculate_action_potential,
    calculate_hamiltonian,
    Psychophysics,
    StressTensor,
)

# Normalization scheme type
NormScheme = Literal["unipolar", "bipolar", "log", "unbounded"]


@dataclass
class DomainConfig:
    """Configuration for a specific data domain."""
    
    name: str
    
    # Normalization bounds for each metric: (low, high)
    bounds: Dict[str, tuple] = field(default_factory=dict)
    
    # Normalization scheme per metric: "unipolar", "bipolar", "log", "unbounded"
    schemes: Dict[str, NormScheme] = field(default_factory=dict)
    
    # Stevens' Law exponents for each metric (optional)
    exponents: Dict[str, float] = field(default_factory=dict)
    
    # Custom normalizers (optional)
    normalizers: Dict[str, Callable[[float], float]] = field(default_factory=dict)


def normalize_value(
    value: float, 
    low: float, 
    high: float, 
    scheme: NormScheme = "unipolar"
) -> float:
    """
    Normalize a value according to the specified scheme.
    
    Args:
        value: Raw input value
        low: Lower bound
        high: Upper bound
        scheme: Normalization scheme
    
    Returns:
        Normalized value (range depends on scheme)
    """
    if high == low:
        return 0.5 if scheme == "unipolar" else 0.0
    
    if scheme == "unipolar":
        # Standard [0, 1] range
        normalized = (value - low) / (high - low)
        return max(0.0, min(1.0, normalized))
    
    elif scheme == "bipolar":
        # [-1, 1] range, centered at midpoint
        midpoint = (low + high) / 2
        half_range = (high - low) / 2
        normalized = (value - midpoint) / half_range
        return max(-1.0, min(1.0, normalized))
    
    elif scheme == "log":
        # Logarithmic scaling for large dynamic range
        # Handles zero and negative by shifting
        safe_low = max(1e-10, low)
        safe_high = max(1e-10, high)
        safe_value = max(1e-10, value)
        
        log_low = math.log10(safe_low)
        log_high = math.log10(safe_high)
        log_value = math.log10(safe_value)
        
        if log_high == log_low:
            return 0.5
        
        normalized = (log_value - log_low) / (log_high - log_low)
        return max(0.0, min(1.0, normalized))
    
    elif scheme == "unbounded":
        # Soft normalization using tanh for unbounded values
        # Maps (-inf, +inf) to (-1, 1), centered at midpoint
        midpoint = (low + high) / 2
        scale = (high - low) / 4  # 4 standard deviations
        
        if scale <= 0:
            return 0.0
        
        # tanh((x - mid) / scale) gives nice S-curve
        normalized = math.tanh((value - midpoint) / scale)
        return (normalized + 1) / 2  # Map to [0, 1]
    
    else:
        # Default to unipolar
        normalized = (value - low) / (high - low)
        return max(0.0, min(1.0, normalized))


# Pre-configured domains
DOMAIN_CONFIGS = {
    "network": DomainConfig(
        name="Network Traffic",
        bounds={
            "bytes": (0, 1_000_000),        # 0 - 1MB
            "packets": (0, 10_000),          # 0 - 10K pps
            "latency_ms": (0, 2000),         # 0 - 2 seconds
            "connections": (0, 1000),        # 0 - 1K concurrent
            "errors": (0, 100),              # 0 - 100%
            "entropy": (0, 8),               # 0 - 8 bits
        },
        exponents={
            "latency_ms": 1.5,  # Expansive: delays feel bigger
            "errors": 3.5,      # Very expansive: errors are painful
        }
    ),
    
    "server": DomainConfig(
        name="Server Metrics",
        bounds={
            "cpu_percent": (0, 100),
            "memory_percent": (0, 100),
            "disk_io": (0, 100_000_000),     # 0 - 100 MB/s
            "network_io": (0, 1_000_000_000), # 0 - 1 Gbps
            "load_average": (0, 16),          # 0 - 16 cores
            "queue_depth": (0, 1000),
        },
        exponents={
            "cpu_percent": 1.1,
            "memory_percent": 1.5,  # Memory pressure feels worse
        }
    ),
    
    "iot": DomainConfig(
        name="IoT Sensors",
        bounds={
            "temperature_c": (-40, 85),
            "humidity_pct": (0, 100),
            "pressure_hpa": (800, 1200),
            "light_lux": (0, 100_000),
            "sound_db": (0, 140),
            "vibration_g": (0, 16),
            "co2_ppm": (0, 5000),
        },
        exponents={
            "temperature_c": 1.0,
            "light_lux": 0.33,   # Compressive like brightness
            "sound_db": 0.67,   # Compressive like loudness
        }
    ),
    
    "financial": DomainConfig(
        name="Financial Markets",
        bounds={
            "price_delta_pct": (-10, 10),
            "volume": (1, 1_000_000_000),
            "volatility": (0, 100),
            "order_imbalance": (-1, 1),
            "spread_bps": (0, 100),
        },
        schemes={
            "price_delta_pct": "bipolar",   # Can be + or -
            "volume": "log",                 # Huge dynamic range
            "order_imbalance": "bipolar",    # Buy/sell imbalance
        },
        exponents={
            "price_delta_pct": 2.0,  # Price moves feel exponential
            "volatility": 1.5,
        }
    ),
    
    "database": DomainConfig(
        name="Database Metrics",
        bounds={
            "query_time_ms": (0, 10_000),
            "rows_returned": (0, 1_000_000),
            "lock_wait_ms": (0, 5000),
            "connections": (0, 500),
            "cache_hit_ratio": (0, 1),
            "deadlocks": (0, 10),
        },
        exponents={
            "query_time_ms": 1.5,
            "lock_wait_ms": 2.0,
            "deadlocks": 3.5,
        }
    ),
    
    "api": DomainConfig(
        name="API Endpoints",
        bounds={
            "response_time_ms": (0, 5000),
            "status_2xx": (0, 100),
            "status_4xx": (0, 100),
            "status_5xx": (0, 100),
            "requests_per_sec": (0, 10_000),
            "payload_bytes": (0, 10_000_000),
        },
        exponents={
            "response_time_ms": 1.5,
            "status_5xx": 3.5,  # Server errors are painful
        }
    ),
}


class UniversalAdapter:
    """
    Universal adapter that "bolts on" to any data source.
    
    Usage:
        adapter = UniversalAdapter(domain="network")
        
        # Feed raw data
        qualia = adapter.process({
            "bytes": 50000,
            "latency_ms": 150,
            "errors": 2,
        })
        
        # qualia is now a PhysicsProfile ready for the AI
    """
    
    def __init__(self, domain: str = "generic", custom_config: Optional[DomainConfig] = None):
        """
        Initialize adapter for a specific domain.
        
        Args:
            domain: Pre-configured domain name or "generic"
            custom_config: Optional custom configuration
        """
        if custom_config:
            self.config = custom_config
        elif domain in DOMAIN_CONFIGS:
            self.config = DOMAIN_CONFIGS[domain]
        else:
            self.config = DomainConfig(name="Generic")
        
        self._history = []
        self._max_history = 100
    
    def normalize(self, metric: str, value: float) -> float:
        """
        Normalize a metric value using the appropriate scheme.
        
        Args:
            metric: Name of the metric
            value: Raw value
        
        Returns:
            Normalized value (range depends on scheme)
        """
        # Check for custom normalizer
        if metric in self.config.normalizers:
            return self.config.normalizers[metric](value)
        
        # Get scheme (default to unipolar)
        scheme = self.config.schemes.get(metric, "unipolar")
        
        # Use bounds if defined
        if metric in self.config.bounds:
            low, high = self.config.bounds[metric]
            return normalize_value(value, low, high, scheme)
        else:
            # Default: assume [0, 100] range for unipolar
            return normalize_value(value, 0, 100, scheme)
    
    def apply_perceptual_scaling(self, metric: str, normalized: float) -> float:
        """
        Apply Stevens' Power Law if exponent is defined.
        
        Args:
            metric: Name of the metric
            normalized: Normalized value [0, 1]
        
        Returns:
            Perceptually scaled value
        """
        if metric in self.config.exponents:
            exponent = self.config.exponents[metric]
            return normalized ** exponent
        return normalized
    
    def process(self, raw_data: Dict[str, float]) -> Dict[str, float]:
        """
        Process raw domain data into physics qualia.
        
        Args:
            raw_data: Dictionary of metric_name -> raw_value
        
        Returns:
            Physics profile (energy, roughness, viscosity, etc.)
        """
        # Step 1: Normalize all inputs
        normalized = {}
        for metric, value in raw_data.items():
            normalized[metric] = self.normalize(metric, value)
        
        # Step 2: Apply perceptual scaling
        perceived = {}
        for metric, value in normalized.items():
            perceived[metric] = self.apply_perceptual_scaling(metric, value)
        
        # Step 3: Map to physics qualia
        qualia = self._compute_qualia(raw_data, normalized, perceived)
        
        # Store history for trend analysis
        self._history.append(qualia)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
        
        return qualia
    
    def _compute_qualia(
        self, 
        raw: Dict[str, float], 
        normalized: Dict[str, float],
        perceived: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Compute physics qualia from processed inputs.
        
        This maps normalized domain data to universal physics metrics.
        """
        # Extract common patterns
        values = list(perceived.values())
        avg_intensity = sum(values) / len(values) if values else 0.0
        max_intensity = max(values) if values else 0.0
        
        # Calculate variance (flux indicator)
        if len(values) > 1:
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
        else:
            variance = 0.0
        
        # Von Mises stress for distortion detection
        is_distortion, von_mises, mean_pressure = StressTensor.is_distortion_anomaly(
            values[:3] if len(values) >= 3 else values + [0.0] * (3 - len(values))
        )
        
        # Build qualia profile
        qualia = {
            # Core physics (isomorphic to all domains)
            "energy": max_intensity,
            "roughness": variance * 2.0,  # Higher variance = rougher texture
            "flux": variance,
            "viscosity": avg_intensity,
            "salience": max_intensity,
            
            # Derived physics
            "dissonance": von_mises,
            "harmony": 1.0 - von_mises,
            "volatility": variance,
            "action": avg_intensity,
            "hamiltonian": avg_intensity + variance,
            
            # Meta-qualia
            "distortion_detected": is_distortion,
            "normalized": normalized,
            "perceived": perceived,
        }
        
        return qualia
    
    def get_trend(self, metric: str = "energy", window: int = 10) -> str:
        """
        Analyze trend over recent history.
        
        Returns:
            "increasing", "decreasing", "stable", or "unknown"
        """
        if len(self._history) < window:
            return "unknown"
        
        recent = [h.get(metric, 0) for h in self._history[-window:]]
        
        # Simple linear regression slope
        n = len(recent)
        sum_x = sum(range(n))
        sum_y = sum(recent)
        sum_xy = sum(i * v for i, v in enumerate(recent))
        sum_x2 = sum(i * i for i in range(n))
        
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return "stable"
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"


def create_adapter(domain: str) -> UniversalAdapter:
    """Factory function to create domain-specific adapter."""
    return UniversalAdapter(domain=domain)


# Convenience aliases
NetworkAdapter = lambda: UniversalAdapter("network")
ServerAdapter = lambda: UniversalAdapter("server")
IoTAdapter = lambda: UniversalAdapter("iot")
FinancialAdapter = lambda: UniversalAdapter("financial")
DatabaseAdapter = lambda: UniversalAdapter("database")
APIAdapter = lambda: UniversalAdapter("api")
