"""Audit helpers backed by an explicitly supplied host memory adapter."""

from typing import Any, Dict, List

from shunollo_core.memory.base import AbstractMemory


def write_audit_log(action: str, details: str, *, memory: AbstractMemory) -> None:
    """Delegate persistence to the host; storage failures propagate to the caller."""
    memory.log_audit(action, details)


def get_recent_audit_logs(limit: int = 100, *, memory: AbstractMemory) -> List[Dict[str, Any]]:
    """Return host audit records without changing their ordering or schema."""
    return memory.get_audit_logs(limit=limit)
