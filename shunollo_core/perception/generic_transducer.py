"""
generic_transducer.py - The Generic Sensory Interface
-----------------------------------------------------
Transforms arbitrary scalar data streams (Financial, IoT, Hardware) into 
Shunollo Sensory Experience using the Physics Engine.

This proves the 'Cognitive Physics' concept:
Input:  [Bitcoin Price] -> [Physics Engine] -> [High Temperature/Roughness] -> [Sensation]
Output: {sound: {timbre: 'noise'}, light: {hue: 0, brightness: 255}}
"""

from collections import deque
from datetime import datetime
from typing import Dict, Any, List
import time

from shunollo_core.models import SensoryInput
from shunollo_core.physics import SensoryPhysics as Phys

class ScalarTransducer:
    """
    A stateful transducer for a single scalar value stream.
    Maintains a rolling window to calculate time-domain physics.
    """
    
    def __init__(self, name: str, window_size: int = 50):
        self.name = name
        self.window_size = window_size
        self.value_buffer: deque = deque(maxlen=window_size)
        self.time_buffer: deque = deque(maxlen=window_size)
        
    def ingest(self, value: float, timestamp: float = None) -> SensoryInput:
        """
        Ingest a scalar value and produce a Sensation.
        """
        if timestamp is None:
            timestamp = time.time()
            
        self.value_buffer.append(value)
        self.time_buffer.append(timestamp)
        
        # 1. Calculate Physics
        physics_profile = self._calculate_physics()
        
        # 2. Map to Sensation (Sound/Light)
        sensation = self._map_physics_to_sensation(physics_profile, value)
        
        return SensoryInput(
            input_type=f"scalar_{self.name}",
            timestamp=datetime.fromtimestamp(timestamp),
            metadata=sensation
        )

    def _calculate_physics(self) -> Dict[str, float]:
        """Apply the Master Sensory Codex to the buffer."""
        values = list(self.value_buffer)
        times = list(self.time_buffer)
        
        if not values: return {}
        
        # Energy
        energy = Phys.Energy.magnitude_rms(values)
        peak = Phys.Energy.peak_impulse(values)
        
        # Time
        tempo = Phys.Time.tempo_hz(times)
        
        # Entropy (Normalize values for Shannon? Or just use Kurtosis/Fractal)
        # For Shannon, we need distribution buckets. Let's use Kurtosis/Fractal for raw scalars.
        roughness = Phys.Entropy.fractal_dimension(values)
        snap = Phys.Entropy.kurtosis(values)
        
        # Quality
        jitter = Phys.Quality.micro_jitter(times)
        
        # State
        # Flow resistance requires Latency, not Value. 
        # For a Scalar stream, 'Flow' might be mapped to Rate of Change (Volatility)
        # Volatility = First Derivative of Amplitude
        volatility = 0.0
        if len(values) >= 2:
            volatility = abs(values[-1] - values[-2])
            
        return {
            "energy": energy,
            "peak": peak,
            "tempo": tempo,
            "roughness": roughness,
            "snap": snap,
            "jitter": jitter,
            "volatility": volatility
        }

    def _map_physics_to_sensation(self, physics: Dict[str, float], current_value: float) -> Dict[str, Any]:
        """
        The 'Synesthesia' Layer: Physics -> Art.
        """
        # --- SOUND ---
        # Roughness (Fractal) -> Timbre/Harmonicity
        # 1.0 (smooth) -> Pure Sine
        # 1.5+ (rough) -> Noise/FM
        fd = physics.get("roughness", 1.0)
        
        if fd < 1.1:
            timbre = "sine"
            fm_mod = 0.0
        elif fd < 1.3:
            timbre = "triangle"
            fm_mod = 0.5
        elif fd < 1.6:
            timbre = "sawtooth"
            fm_mod = 5.0
        else:
            timbre = "square" # Harsh
            fm_mod = 20.0 # Metallic noise
            
        # Volatility -> Pitch Modulation (Vibrato?)
        # For now, let's map Value -> Pitch directly (High price = High pitch)
        # Normalize assuming 0-100 range for demo, or dynamic scaling
        pitch = 200 + (current_value * 10) # 10.0 -> 300Hz
        
        # Snap (Kurtosis) -> Transient (Volume spike)
        snap = physics.get("snap", 0.0)
        volume = max(0.2, min(1.0, 0.5 + (snap / 10.0)))

        sound = {
            "pitch": int(pitch),
            "volume": float(volume),
            "timbre": timbre,
            "fm_modulation": float(fm_mod),
            "duration": 0.2
        }

        # --- LIGHT ---
        # Energy -> Brightness
        brightness = int(min(255, physics.get("energy", 0) * 10))
        
        # Jitter -> Strobe (Pulse Rate)
        jitter = physics.get("jitter", 0)
        pulse = 1
        if jitter > 0.1: pulse = 5 # Strobe on unstable timing
        if jitter > 0.5: pulse = 10
        
        # Temperature (proxied by Roughness/Volatility) -> Hue
        # Smooth/Stable = Blue (240). Rough/Volatile = Red (0).
        heat_score = (fd - 1.0) * 2.0 # 1.0->0, 1.5->1.0
        heat_score = max(0.0, min(1.0, heat_score))
        
        hue = int(240 * (1.0 - heat_score)) # 240 (Blue) -> 0 (Red)
        
        light = {
            "hue": hue,
            "brightness": brightness,
            "saturation": 1.0,
            "pulse_rate": pulse
        }
        
        return {
            "sound": sound, 
            "light": light, 
            "physics": physics # Expose raw physics for Agents
        }
