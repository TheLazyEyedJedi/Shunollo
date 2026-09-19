from unittest.mock import Mock

import pytest

from shunollo_core.feedback.audit_log import get_recent_audit_logs, write_audit_log
from shunollo_core.memory.base import AbstractMemory


def test_explicit_host_write_and_read():
    memory = Mock(spec=AbstractMemory)
    records = [{"action": "review", "details": "host-owned", "host_id": 7}]
    memory.get_audit_logs.return_value = records
    write_audit_log("review", "host-owned", memory=memory)
    memory.log_audit.assert_called_once_with("review", "host-owned")
    assert get_recent_audit_logs(12, memory=memory) is records
    memory.get_audit_logs.assert_called_once_with(limit=12)


def test_default_limit_and_host_isolation():
    first, second = Mock(spec=AbstractMemory), Mock(spec=AbstractMemory)
    first.get_audit_logs.return_value = [{"action": "first"}]
    second.get_audit_logs.return_value = []
    write_audit_log("first", "details", memory=first)
    assert get_recent_audit_logs(memory=first) == [{"action": "first"}]
    assert get_recent_audit_logs(memory=second) == []
    first.get_audit_logs.assert_called_once_with(limit=100)
    second.log_audit.assert_not_called()


@pytest.mark.parametrize("operation", ["read", "write"])
def test_host_errors_are_not_hidden(operation):
    memory = Mock(spec=AbstractMemory)
    error = OSError("Host storage unavailable")
    memory.log_audit.side_effect = error
    memory.get_audit_logs.side_effect = error
    with pytest.raises(OSError) as caught:
        if operation == "write":
            write_audit_log("review", "details", memory=memory)
        else:
            get_recent_audit_logs(memory=memory)
    assert caught.value is error


def test_no_implicit_storage_fallback():
    with pytest.raises(TypeError, match="memory"):
        write_audit_log("review", "details")
    with pytest.raises(TypeError, match="memory"):
        get_recent_audit_logs()
