"""feedback_store.py – simple JSONL feedback persistence"""

import json, datetime, pathlib
from typing import Dict, Any

FEEDBACK_DIR = pathlib.Path(__file__).resolve().parent
FEEDBACK_FILE = FEEDBACK_DIR / "agent_feedback.jsonl"

def save_feedback(feedback: Dict[str, Any]) -> None:
    """Append a feedback dict as JSON line with timestamp."""
    feedback.setdefault("timestamp", datetime.datetime.now(datetime.timezone.utc).isoformat())
    with FEEDBACK_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(feedback) + "\n")
