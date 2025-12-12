import time
from dataclasses import dataclass, asdict


@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: float
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_dict(self):
        d = asdict(self)
        # Ensure JSON-serializable numeric types
        d["amount"] = float(d["amount"])
        return d
