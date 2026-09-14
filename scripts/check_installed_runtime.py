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
    print("Installed signal model and runtime audit persistence: PASS")


if __name__ == "__main__":
    main()
