import hashlib
import time


class ProofOfHistory:
    """
    Very small proof-of-history simulation: keep a rolling digest that is updated
    each time an event is recorded. The digest is the SHA256 of previous_digest + timestamp.
    """

    def __init__(self):
        self.last_digest = hashlib.sha256(b"TriadPoH").hexdigest()
        self.counter = 0

    def record_event(self) -> str:
        self.counter += 1
        payload = f"{self.last_digest}:{time.time()}:{self.counter}".encode("utf-8")
        self.last_digest = hashlib.sha256(payload).hexdigest()
        return self.last_digest
