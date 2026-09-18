"""Run with an isolated installed-wheel Python (-I), outside source imports."""

import tempfile
from pathlib import Path

import shunollo_runtime
from shunollo_core.models import ShunolloSignal
from shunollo_runtime.audit import SQLiteAuditMiddleware


def main():
    source_root = Path(__file__).resolve().parents[1]
    installed_path = Path(shunollo_runtime.__file__).resolve()
    assert source_root not in installed_path.parents, installed_path
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "audit.sqlite"
        with SQLiteAuditMiddleware(path) as audit:
            audit.on_publish("scalar", {"vector": ShunolloSignal(energy=0.5).to_vector()})
            audit.on_receive("support", {"ticket_id": "example"})
        with SQLiteAuditMiddleware(path) as audit:
            rows = audit.records()
            assert len(rows) == 2
            assert len(rows[0]["payload"]["vector"]) == 18
            assert rows[1]["payload"] == {"ticket_id": "example"}
    from shunollo_core.perception.meta_gene_layer import TraitMemory, summary
    assert summary("new-host")["top_traits"] == []
    first, second = TraitMemory(), TraitMemory()
    first.reconstruct_state({"observer": {"warm_bright": {"count": 3}}})
    assert first.trait_profile("observer") == {"warm": 3, "bright": 3}
    assert second.trait_profile("observer") == {}
    from shunollo_core.perception.generic_transducer import ScalarTransducer
    scalar = ScalarTransducer('installed', value_scale=10)
    scalar.ingest(2, 1000)
    signal = scalar.ingest(4, 1002)
    assert signal.frequency == 0.5 and len(signal.to_vector()) == 18
    assert signal.metadata['mapping_version'] == 'scalar-v2'
    import numpy as np
    from shunollo_core.brain.autoencoder import Autoencoder
    from shunollo_core.brain.neural_net import LinearAssociativeMemory
    imagination = Autoencoder()
    sample = np.zeros(18)
    sample[0] = np.nan
    imagination.train_on_normal(sample)
    assert np.isfinite(imagination.calculate_anomaly_score(sample))
    with tempfile.TemporaryDirectory() as directory:
        brain = LinearAssociativeMemory(input_size=4, reservoir_size=8)
        path = Path(directory) / 'brain'
        brain.save(path)
        restored = LinearAssociativeMemory()
        restored.load(path)
        restored.reset()
        assert restored.forward(np.zeros(4))['classification_score'] == .5
    print("Installed signal model, audit persistence and isolated trait reconstruction: PASS")


if __name__ == "__main__":
    main()
