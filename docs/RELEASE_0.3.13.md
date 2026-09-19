# Shunollo 0.3.13

Maintenance release repairing the legacy Core audit helper's import of removed SQL storage.

- Audit helpers now use an explicitly supplied host AbstractMemory adapter.
- Reads preserve host schema and ordering; host storage errors propagate.
- No default database, global adapter, application imports or data migration is introduced.
- Installed-wheel verification now exercises the audit helper.

Compatibility: callers of write_audit_log and get_recent_audit_logs must supply memory= explicitly. The module previously failed to import. See HOST_AUDIT_LOG.md. Optional runtime transport auditing is unchanged. Physics, scoring and scalar-v2 mapping are unchanged.

Validation: 284 engine tests and installed-package verification passed for the repair; release CI verifies Python 3.10–3.12 and clean installed wheels. Consumers should upgrade their pinned published dependency separately.
