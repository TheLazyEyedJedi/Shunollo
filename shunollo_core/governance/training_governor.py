"""
training_governor.py – Decides when to trigger agent retraining.
"""

import time
from typing import Optional
from shunollo_core.memory.base import AbstractMemory

class TrainingGovernor:
    # Thresholds
    import os
    # Thresholds
    MIN_FEEDBACK_ITEMS = int(os.getenv("GOVERNOR_MIN_ITEMS", 50))
    MIN_TIME_INTERVAL_SECONDS = int(os.getenv("GOVERNOR_MIN_SECONDS", 3600))

    def __init__(self, memory: AbstractMemory):
        self.memory = memory
        self.last_train_ts = 0.0
        # In a real system, we'd load this from a 'system_state' table
        self._load_state()

    def _load_state(self):
        # Look for last "training_run" in audit logs
        try:
             logs = self.memory.get_audit_logs(limit=500)
             for log in logs:
                 if log["action"] == "training_run":
                     self.last_train_ts = log["timestamp"]
                     break
        except Exception:
             # If memory not ready or empty
             pass

    def should_retrain(self) -> bool:
        """
        Returns True if we have enough new data AND enough time has passed.
        """
        now = time.time()
        
        # 1. Time Check
        if (now - self.last_train_ts) < self.MIN_TIME_INTERVAL_SECONDS:
            return False

        # 2. Data Check
        try:
            recent_fb = self.memory.get_recent_cluster_feedback(limit=self.MIN_FEEDBACK_ITEMS + 10)
            new_feedback_count = sum(1 for fb in recent_fb if fb["timestamp"] > self.last_train_ts)
            return new_feedback_count >= self.MIN_FEEDBACK_ITEMS
        except Exception:
            return False

    def log_training_run(self, details: str = "Automated"):
        self.last_train_ts = time.time()
        self.memory.log_audit("training_run", details)

    def safety_check(self, proposed_updates: dict) -> bool:
        """
        COSMOS INSTITUTE AUDIT:
        Prevents 'Value Drift' where the AI learns to be useless or malicious based on bad feedback.
        """
        # 1. Radical Shift Check
        # If any agent shifts by more than 0.3 in one go, veto it.
        for name, weight in proposed_updates.items():
            current = self.memory.get_weight(name)
            if abs(current - weight) > 0.3:
                self.memory.log_audit("training_veto", f"Radical shift detected for {name}")
                return False
                
        # 2. Lobotomy Check
        # If all agents drop below 0.1, the system is essentially killing itself.
        avg_weight = sum(proposed_updates.values()) / len(proposed_updates)
        if avg_weight < 0.1:
            self.memory.log_audit("training_veto", "System Lobotomy detected (Low Trust)")
            return False
            
        return True
