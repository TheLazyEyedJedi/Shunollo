# Optional elapsed-time smoothing (unreleased)

`VestibularDynamics.integrate_elapsed(value, dt=seconds)` uses the constructor's
`time_constant` as an e-folding time in seconds. A constant input applied over the
same duration has the same endpoint across different sampling rates, within floating
point tolerance. Piecewise-changing signals require consistent sample/hold semantics.

The existing `integrate_acceleration(value)` keeps its original per-call damping
behavior. There is no automatic mode switch or reinterpretation of old callers.
Choose one method per stream. Missing observations, session changes and gap resets
are host policy, not inferred by this primitive. Invalid inputs do not mutate state.

For an old reference damping d at interval h, the equivalent time constant is
`-h / log(d)` for 0 < d < 1. Do not silently substitute the constructor default of
10 seconds for an application's existing reference cadence. Both modes are optional
analysis/presentation operations; neither is a required step in data translation.
The complete precise sequence can be inverted with known state and parameters;
quantization, discarded samples or a final value alone can prevent recovery.

This change is source-only and unreleased. Applications continue importing their
published versions until an explicit release and dependency update is tested.
