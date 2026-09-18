"""Bounded scalar-stream adapter for the public ShunolloSignal interface.

Mapping v2 replaces the removed SensoryInput/SensoryPhysics APIs. Input units
are caller-defined; value_scale fixes normalization without fitting on future
samples. This adapter measures stream properties, not domain-specific threats.
"""
from collections import deque
from datetime import datetime, timezone
import math
import time

import numpy as np

from shunollo_core.interfaces import BaseTransducer
from shunollo_core.models import ShunolloSignal
from shunollo_core import physics
from shunollo_core.perception.auditory_cortex import AuditoryCortex


class ScalarTransducer(BaseTransducer):
    mapping_version = 'scalar-v2'

    def __init__(self, name: str, window_size: int = 50, *, value_scale: float = 100.0,
                 flux_scale: float = 1.0):
        if not isinstance(name, str) or not name.strip():
            raise ValueError('name must be a nonempty string')
        if type(window_size) is not int or not 2 <= window_size <= 4096:
            raise ValueError('window_size must be an integer in [2, 4096]')
        for value in (value_scale, flux_scale):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError('normalization scales must be finite and positive')
        self.name, self.window_size = name, window_size
        self.value_scale, self.flux_scale = float(value_scale), float(flux_scale)
        self.value_buffer = deque(maxlen=window_size)
        self.time_buffer = deque(maxlen=window_size)
        self._auditory = AuditoryCortex()

    def reset(self):
        self.value_buffer.clear()
        self.time_buffer.clear()

    def ingest(self, value: float, timestamp: float = None) -> ShunolloSignal:
        timestamp = time.time() if timestamp is None else timestamp
        for item in (value, timestamp):
            if isinstance(item, bool) or not isinstance(item, (int, float)) or not math.isfinite(item):
                raise ValueError('value and timestamp must be finite numbers')
        if self.time_buffer and timestamp - self.time_buffer[-1] < 1e-6:
            raise ValueError('timestamps must increase by at least one microsecond; reset for a new stream')
        try:
            observed_at = datetime.fromtimestamp(timestamp, timezone.utc)
        except (ValueError, OverflowError, OSError) as exc:
            raise ValueError('timestamp is outside the supported datetime range') from exc
        # Validation precedes state mutation. Raw finite values are kept for callers.
        self.value_buffer.append(float(value))
        self.time_buffer.append(float(timestamp))
        values = np.clip(np.asarray(self.value_buffer), -self.value_scale, self.value_scale) / self.value_scale
        times = np.asarray(self.time_buffer)
        deltas = np.diff(times)
        entropy = physics.calculate_entropy(values)
        energy = float(np.sqrt(np.mean(values * values)))
        tempo = float((len(times)-1)/(times[-1]-times[0])) if len(times)>1 else 0.
        jitter = float(np.std(deltas)) if len(deltas)>1 else 0.
        cv = jitter/float(np.mean(deltas)) if len(deltas)>1 else 0.
        derivative = abs(float(values[-1]-values[-2]))/float(deltas[-1]) if len(deltas) else 0.
        # All arithmetic uses bounded values; normalize before applying Core flux.
        normalized_flux = min(1., derivative / self.flux_scale)
        signal = ShunolloSignal(input_type='scalar_'+self.name, timestamp=observed_at,
            energy=energy, entropy=entropy, frequency=tempo,
            roughness=float(physics.calculate_roughness(entropy,jitter=jitter*1000)),
            volatility=float(np.std(values)), harmony=1./(1.+cv),
            flux=float(physics.calculate_flux(normalized_flux,limit=1.)))
        sound = self._auditory.process_sound(signal)
        # Core's renderer expects hue in degrees. Use a consistent 0..1 signal
        # hue so ShunolloSignal.to_vector() does not saturate all colored inputs.
        signal.hue = (240./360.) * (1.-signal.roughness)
        signal.saturation = 1.
        profile = dict(energy=energy, peak=float(np.max(np.abs(values))), tempo=tempo,
                       roughness=signal.roughness, jitter_seconds=jitter,
                       volatility=signal.volatility, absolute_derivative=derivative, flux=signal.flux)
        signal.metadata = dict(raw_value=float(value),mapping_version=self.mapping_version,
            sample_count=len(values), temporal_available=len(values)>1,
            normalization={'value_scale':self.value_scale,'flux_scale':self.flux_scale,
                           'clipped_samples':sum(abs(v)>self.value_scale for v in self.value_buffer)},
            physics=profile, sound=sound,
            light={'hue':signal.hue*360,'saturation':signal.saturation,'brightness':energy*255})
        return signal
