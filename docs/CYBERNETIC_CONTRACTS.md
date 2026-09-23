# Cybernetic memory contracts (0.3.14 source)

This change repairs generic symbolic feedback and recall boundaries. It does not
train a language model, connect a network application, or certify detection.

- `perception.encoding.Codon` represents versioned, modality-labeled structured
  traits. `None` means unknown. Canonical tokens preserve trait boundaries.
- `decode_legacy` wraps an entire legacy token as opaque data. Historical tokens
  cannot generally be split on underscores without losing meaning.
- `feedback.training_loop.apply_feedback` now takes explicit traits and a
  host-owned `TraitMemory`; importing it no longer relies on a missing function.
- `percept_genome.update_weights` requires an explicit host memory adapter and
  fails before mutation when omitted. Explicit adapter reads do not reuse another
  host's cached weights. This repairs previously broken calls, not LLM training.
- Hippocampus validates exactly 18 finite query dimensions, nonnegative result
  counts and thresholds. Infinity remains supported for nearest-neighbor novelty.
  Cold loading retains a bounded deque rather than reading the whole file into
  memory. Append-only storage retention remains host policy and is not yet bounded
  by this change.

The historical domain-specific `codon_builder` remains for compatibility. New
hosts should use structured generic traits and own their domain classification.
Existing vector normalization and legacy encoding outputs are unchanged.

The generic codon-weight reader delegates caching to the owning adapter;
agent-name-only process caches could leak values between different hosts.

Validation: 293 engine tests passed locally before package publication. This is
source work until the independently built wheel is released; applications must
not substitute a sibling editable install for a published dependency.
