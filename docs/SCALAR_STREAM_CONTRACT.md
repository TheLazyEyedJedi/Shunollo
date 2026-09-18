# Scalar stream interface repair (unreleased)

The published 0.3.11 `perception.generic_transducer` imports removed `SensoryInput` and `SensoryPhysics` APIs. This repair uses the existing `BaseTransducer` / `ShunolloSignal` contract and supported physics functions. It does not add application-specific semantics or silently recreate obsolete facades.

```python
from shunollo_core.perception.generic_transducer import ScalarTransducer
stream = ScalarTransducer('temperature', window_size=50, value_scale=100)
stream.ingest(20, timestamp=1000)
signal = stream.ingest(25, timestamp=1002)
assert signal.frequency == 0.5
sound, light = signal.metadata['sound'], signal.metadata['light']
```

Mapping `scalar-v2` is explicit because the former implementation was not executable against current public APIs. Sample count is bounded (2–4096). Signed input is clipped to a caller-supplied fixed scale and normalized to [-1,1]. Energy is normalized RMS; entropy is the discrete distribution entropy of normalized samples; roughness uses Core entropy/jitter mapping; volatility is standard deviation. Frequency is (sample_count-1)/elapsed seconds. Flux is the latest absolute normalized-value derivative divided by `flux_scale` and clipped through Core. Inter-arrival jitter and harmony retain timing information.

The window is a sample-count window, not a fixed-duration traffic window. No packet/domain concepts are added. Timestamps use epoch seconds, return aware UTC datetimes, and must increase by at least one microsecond. Values/scales must be finite; normalization scales must be positive. Invalid input leaves the buffers unchanged. Call `reset()` or use a new instance for a different stream. Caller-supplied timestamps are recommended for replay; omitted timestamps use the wall clock.

The signal's hue is normalized to [0,1] for `to_vector`; metadata light hue uses degrees for Core's existing renderer. Audio parameters use `AuditoryCortex`. Clipping counts, normalization configuration, temporal availability and measurements are retained in metadata. No learned threshold, calibrated threat probability or performance gain is implied.

A related contract defect in `query_neural_intuition` is also repaired: it now extracts the scalar classification score from the reservoir's result dictionary. The previous helper nested a dictionary where its documented callers expected a number. This does not train the reservoir; an untrained readout still yields 0.5, and the reservoir's own anomaly field remains a placeholder. Autoencoder reconstruction error is a separate quantity.

Ten regressions cover the scalar adapter and neural query contract. The existing installed-wheel check now exercises the scalar stream outside the source tree.

## Release boundary

This is an unreleased source repair. The published 0.3.11 wheel is unchanged, and Omnisthesia remains pinned to that release. Publish a new version and test the application's installed-wheel dependency before replacing its broken duplicate scalar wrapper with this adapter. Do not copy engine implementation into Omnisthesia.
