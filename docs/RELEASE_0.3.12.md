# Shunollo 0.3.12

Maintenance release for the independently installed, domain-agnostic engine.

- Repair the public scalar stream transducer and numeric neural query result.
- Harden neural training, input validation, random-state isolation and checkpoint loading.
- Include runtime audit persistence and isolated trait reconstruction repairs validated by the installed-wheel check.
- Require Python 3.10 or newer.

Compatibility: scalar mapping is explicitly versioned `scalar-v2`; corrupt existing neural checkpoints now raise exceptions. Missing checkpoint files remain a no-op. These changes do not establish calibrated threat probabilities or sound/light detection superiority. See PRE_RELEASE_REVIEW.md and SCALAR_STREAM_CONTRACT.md for detailed contracts and limits.

Verification before publication: 279 Core tests; Python 3.10–3.12 CI; isolated installed-wheel checks. Omnisthesia dependency migration is a separate change after package publication.
