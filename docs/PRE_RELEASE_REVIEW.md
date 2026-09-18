# Pre-release review — 2026-09-18

Reviewed source after PR #10 (70ca9b7). This review targets neural numerical behavior, state isolation, checkpoint integrity and installed-package compatibility. It does not establish detection accuracy or complete coverage of every experimental feature.

## Additional fixes

- Autoencoder inference sanitized NaN/Inf, but loss and training reused the original invalid sample. Loss could become non-finite and training could permanently poison weights. All three paths now use the same sanitized single observation; the established zero-replacement policy remains unchanged.
- Both neural constructors reset NumPy's process-global random generator. A local RandomState preserves deterministic initial weights without affecting callers' experiment sampling.
- Reservoir input broadcasting could mutate recurrent state before rejecting a multi-column input. Both models now accept only a vector or one-column observation, validating before mutation. Batching is not supported.
- Invalid classifier targets could poison the readout. Targets must be finite and in [0,1], checked before the recurrent forward step.
- Checkpoint loading could partially overwrite a live model, accepted inconsistent/non-finite arrays, and retained stale dimensions. Loading now validates the complete checkpoint before committing, adopts its dimensions, and accepts pathlib paths. Historical missing reservoir bias fields remain supported. Missing files remain a no-op. Corrupt existing files now raise an exception instead of merely printing and continuing; callers should explicitly handle checkpoint errors.
- Python metadata claimed 3.9 support although runtime annotations require 3.10. The minimum is now 3.10, matching the existing CI matrix (3.10–3.12).

## Verification

23 new regression cases: 17 fail against the earlier inventory source, six already pass. Updated source: **279 passed**, with one existing holographic-capacity warning. Rebuilt wheel installed into an isolated environment passes the extended installed-runtime check, including invalid-sample training and dimension-changing checkpoint restoration. No source-tree imports are used by that check. GitHub matrix results are attached to the pull request.

## Release and remaining scope

No version bump, tag or publication is included. The local verification wheel retains the source version 0.3.11; it is not the published wheel. Omnisthesia remains on published 0.3.11 and must be tested against the new published engine before its dependency is upgraded.

Neural inputs are expected to be normalized by the transducer. Zero replacement for non-finite observations is compatibility behavior, not evidence that missing data is benign. Finite extreme magnitudes, mutated model parameters and concurrent use of the same instance are not validated as supported workloads. Global neural factories still return shared state; use separate model instances for independent experiments. Classifier scores are not calibrated probabilities; the reservoir's anomaly field remains a placeholder and the autoencoder reports reconstruction error. Existing hue-unit differences, legacy event-routing paths and optional-feature wiring remain separate migration work documented in Omnisthesia's capability inventory. This repair makes no sound/light detection-superiority claim.
