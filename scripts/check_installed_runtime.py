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
    print("Installed signal model, audit persistence and isolated trait reconstruction: PASS")


if __name__ == "__main__":
    main()
