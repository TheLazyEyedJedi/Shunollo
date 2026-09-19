# Host-owned audit logging

The Core audit helpers require an explicit `AbstractMemory` adapter:

```python
from shunollo_core.feedback.audit_log import write_audit_log, get_recent_audit_logs

# memory is the host application's AbstractMemory implementation.
write_audit_log("review_completed", "review-123", memory=memory)
records = get_recent_audit_logs(limit=25, memory=memory)
```

Writes call `memory.log_audit`; reads call `memory.get_audit_logs`. The host owns persistence, record schema, ordering, validation, retention and access controls. Errors propagate unchanged. Core introduces no default database, file path or global adapter, and does not claim tamper resistance or transactional guarantees.

Previously this module failed to import because it referenced removed `shunollo_core.storage.database`. Callers must now supply `memory=` explicitly; there is no silent fallback to historical storage. This is separate from optional `shunollo_runtime.audit.SQLiteAuditMiddleware`, which records transport observations.

This repair is unreleased. Omnisthesia remains pinned to published 0.3.12 until a separate engine release and tested consumer upgrade. No database migration or package version change is included.
