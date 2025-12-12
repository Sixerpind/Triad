import hashlib
import json
import time
from typing import List, Any


class Block:
    def __init__(self, index: int, transactions: List[dict], prev_hash: str, pow_checkpoint: bool = False):
        self.index = int(index)
        self.transactions = list(transactions)
        self.prev_hash = str(prev_hash)
        self.pow_checkpoint = bool(pow_checkpoint)
        self.timestamp = time.time()
        self.nonce = 0
        self.hash = self.compute_hash()
        # votes and double_voters may be attached by consensus
        self.votes = []
        self.double_voters = set()

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "transactions": self.transactions,
            "prev_hash": self.prev_hash,
            "pow_checkpoint": self.pow_checkpoint,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "hash": self.hash,
        }

    def compute_hash(self) -> str:
        payload = {
            "index": self.index,
            "transactions": self.transactions,
            "prev_hash": self.prev_hash,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "pow_checkpoint": self.pow_checkpoint,
        }
        payload_bytes = json.dumps(payload, sort_keys=True, separators=(",":":"), ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(payload_bytes).hexdigest()

    def proof_of_work(self, difficulty: int = 4, max_attempts: int = 10_000_00) -> str:
        """
        Simple proof-of-work: find a nonce so that hash starts with difficulty zeros.
        Returns resulting hash.
        """
        assert difficulty >= 0
        prefix = "0" * difficulty
        attempts = 0
        while attempts < max_attempts:
            self.nonce = attempts
            self.timestamp = time.time()
            h = self.compute_hash()
            if h.startswith(prefix):
                self.hash = h
                return h
            attempts += 1
        raise RuntimeError(f"Proof-of-work failed after {max_attempts} attempts")

    # Alias for code that called a different name previously
    def mine(self, difficulty: int = 4):
        return self.proof_of_work(difficulty)
