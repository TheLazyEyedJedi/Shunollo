# shunollo_core/feedback/audit_log.py

import os, time
from datetime import datetime
from shunollo_core.storage.database import write_audit_log_db, get_audit_logs_db

def write_audit_log(action: str, details: str):
    """
    Write an audit log entry to the database.
    """
    write_audit_log_db(action, details)

def get_recent_audit_logs(limit: int = 100):
    """
    Retrieve the most recent audit log entries from the database.
    """
    return get_audit_logs_db(limit=limit)
