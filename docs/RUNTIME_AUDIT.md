# Runtime signal audit adapter

SQLiteAuditMiddleware records the payloads seen by the existing Thalamus
middleware hooks. It lives in shunollo_runtime; Core does not import it or gain
database dependencies. Its implementation uses the Python standard library.

```python
from shunollo_runtime.audit import SQLiteAuditMiddleware
from shunollo_runtime.thalamus import RedisThalamus

# Explicitly choose an application-owned path with an existing parent directory.
with SQLiteAuditMiddleware("signals.sqlite") as audit:
    transport = RedisThalamus(middleware=[audit])
    transport.publish_stimulus("sensor", {"energy": 0.5})
    records = audit.records(after_id=0, limit=100)
```

The Redis example requires a configured Redis service. The adapter tests and
installed-wheel check use local calls and require no Redis service.

Each record contains a monotonically increasing database ID, observation time,
direction, channel, and a JSON payload snapshot. Read subsequent pages using the
last record's ID. The transport passes payloads through unchanged. Physical
units and domain interpretation remain the caller's responsibility.

An observation is **not a delivery receipt**. Publish hooks run before the
transport sends; later middleware may also modify payloads. This adapter does
not offer exactly-once delivery, retry deduplication, retention, or tamper-proof
logging. It does not replace application-specific history tables. Applications
must decide which data to record and how long to retain it.

Values must be JSON-compatible; NaN, infinity and unserializable values fail
before insertion. Audit errors propagate to the caller's transport policy
(RedisThalamus catches hook errors and returns a failed send). Call close(), or
use a context manager, after all threads using the adapter have completed.

The CI wheel check installs the root project's shunollo distribution into a
clean virtual environment and runs with isolated imports. This verifies the
currently shipped combined distribution, not a separately published Core or
runtime package. Separate distribution ownership and legacy storage migration
remain subsequent work.
