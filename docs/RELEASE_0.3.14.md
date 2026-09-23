# Shunollo 0.3.14

Generic symbolic memory repairs and an optional count-preserving image channel.

- Structured, versioned codons preserve modality, mapping, trait names and units.
  The explicit legacy decoder preserves ambiguous tokens as opaque values.
- Symbolic feedback uses explicit host-owned memory. Weight reads no longer use
  an agent-name cache shared across host adapters.
- Episodic recall validates vector dimensions and limits; cold loading retains a
  bounded recent cache. Hosts still own durable retention policy.
- `perception.count_image.encode_counts` and `decode_counts` preserve integer
  counts in a one-row 16-bit PNG, with strict range and size bounds. The mapping
  is `count-image-u16-v1`. Callers retain time units, coverage and source identity.
- Dependency metadata now correctly requires Pydantic 2.

Migration: `apply_feedback` requires explicit `traits` and `memory` arguments;
`percept_genome.update_weights` requires `memory`. These repair previously broken
implicit calls. Existing sensory mappings and legacy encoding outputs remain.

The count channel is domain-independent; it does not infer observation coverage
or threat labels. This release makes no detection, LLM training or biological
equivalence claims. Application orchestration, network interpretation and private
research data are not included.
