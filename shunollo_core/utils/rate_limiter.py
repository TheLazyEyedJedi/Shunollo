"""
rate_limiter.py - The Synaptic Gate (Cost Control)
--------------------------------------------------
Biological Role: Inhibitory Neurons. They prevent the brain from firing too rapidly (Seizures/Burnout).
Technical Role:  Token Bucket algorithm to limit API calls (e.g., 5 calls per hour).
"""
import time
import threading

class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        """
        :param capacity: Max tokens the bucket can hold (Burst limit).
        :param refill_rate: Tokens added per second.
        """
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        """Attempt to consume tokens. Returns True if successful."""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_refill
            
            # Refill
            new_tokens = elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_refill = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

# Global Limiter: 5 calls per hour (approx 1 per 720 secs)
# Refill rate = 5 / 3600 = 0.00138 per sec
_LLM_LIMITER = TokenBucket(capacity=2, refill_rate=5/3600)

def can_consult_oracle():
    """Check if we have budget to call the LLM."""
    return _LLM_LIMITER.consume(1)
