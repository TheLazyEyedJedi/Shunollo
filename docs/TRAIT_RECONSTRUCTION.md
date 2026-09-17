# Explicit trait reconstruction

The published 0.3.10 implementation calls `codon_memory.get_all_memory`, which that release no longer exports. This prevents both cold-start adaptation and trait summaries from working.

The repair removes implicit persistence access. A new `TraitMemory` object owns in-memory counts; the host explicitly selects and supplies a snapshot. Independent objects isolate applications or sessions. Existing module-level functions remain as a single-process convenience interface, starting empty.

```python
from shunollo_core.perception.meta_gene_layer import TraitMemory

traits = TraitMemory()
traits.reconstruct_state({"observer": {"warm_bright": {"count": 3}}})
traits.adapt("observer", ["steady"])
print(traits.summary("observer"))
```

Reconstruction replaces state atomically and preserves legacy underscore tokenization. A missing snapshot explicitly resets state to empty. Invalid entries leave old state intact. Snapshot counts are nonnegative integers; learned weights are not converted into counts or treated as accuracy evidence. Incremental deprecation can still produce negative trait balances, preserving the prior API's behavior.

Persistence, database queries, naming conventions and domain interpretation remain the host's responsibility. This module imports no application, SQL storage, or legacy codon-memory API. Returning a summary of an empty default object does not mean historical persistence has been restored.

## Release and consumer gate

This source fix does not change the already published `shunollo==0.3.10` artifact. Keep Omnisthesia's trait feature explicitly unavailable until a new engine version is published and its installed wheel is verified. No version number is advanced or package uploaded by this change.

Before enabling it in Omnisthesia: select an audited source of actual trait counts (the full preserved legacy entry contains counts; the weight-only export does not), build an app-owned snapshot adapter, test separate host instances and restart reconstruction, then validate the UI and bump the dependency to the verified release. Do not restore the bundled engine or monkey-patch Core to bypass that release boundary.
