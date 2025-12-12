from .block import Block
import math
from typing import List, Set

class FederatedConsensus:
    """
    Simple federated consensus with quorum voting simulation and conflict resolution.

    New features:
    - propose_conflicting: create multiple conflicting block proposals with explicit vote lists
    - detect double-voters (validators voting for more than one proposal)
    - resolve_conflict: choose the block that reaches quorum after excluding double-voters

    Notes:
    - Votes are simulated lists of validator ids. In real-world, votes must be signed
      and double-voting should be provable and subject to slashing.
    """

    def __init__(self, validators, quorum_fraction=0.51):
        if not validators:
            raise ValueError("validators list must not be empty")
        self.validators = list(validators)
        self.quorum_fraction = float(quorum_fraction)

    def _simulate_votes(self) -> List[str]:
        """Simulate votes from all validators. """
        return list(self.validators)

    def vote(self, chain, transactions):
        prev_hash = chain[-1].hash
        votes = self._simulate_votes()
        new_block = Block(
            index=len(chain),
            transactions=[tx.to_dict() for tx in transactions],
            prev_hash=prev_hash,
            pow_checkpoint=False,
        )
        new_block.votes = votes
        return new_block

    def propose_conflicting(self, chain, transactions, split_votes: List[List[str]]):
        """
        Create multiple conflicting block proposals based on explicitly provided vote lists.
        split_votes should be a list where each entry is the list of validators voting for that proposal.
        Returns list of Block objects (proposals).
        """
        proposals = []
        prev_hash = chain[-1].hash
        for votes in split_votes:
            blk = Block(
                index=len(chain),
                transactions=[tx.to_dict() for tx in transactions],
                prev_hash=prev_hash,
                pow_checkpoint=False,
            )
            blk.votes = list(votes)
            proposals.append(blk)
        return proposals

    def _detect_double_voters(self, blocks: List[Block]) -> Set[str]:
        """Return validators that voted for more than one block in the provided proposals."""
        seen = {}
        for idx, b in enumerate(blocks):
            for v in set(getattr(b, "votes", [])):
                seen.setdefault(v, []).append(idx)
        double = {v for v, idxs in seen.items() if len(idxs) > 1}
        return double

    def validate_votes(self, block):
        """Validate that the block has enough votes to reach quorum (no double-vote detection)."""
        if not hasattr(block, "votes"):
            return False
        votes = set(block.votes)
        valid_votes = len([v for v in votes if v in self.validators])
        required = max(1, math.ceil(len(self.validators) * self.quorum_fraction))
        return valid_votes >= required

    def validate_votes_excluding(self, block, excluded_voters: Set[str]):
        """Validate votes for a block excluding any validators listed in excluded_voters."""
        if not hasattr(block, "votes"):
            return False
        votes = set(block.votes) - set(excluded_voters)
        valid_votes = len([v for v in votes if v in self.validators])
        required = max(1, math.ceil(len(self.validators) * self.quorum_fraction))
        return valid_votes >= required

    def resolve_conflict(self, blocks: List[Block]):
        """
        Resolve a set of conflicting block proposals.
        - Detect validators that double-voted and exclude their votes.
        - Choose the first block that reaches quorum after excluding double-voters.
        - If multiple meet quorum, choose the one with the highest valid votes.
        - If none meet quorum, raise RuntimeError.
        """
        if not blocks:
            raise ValueError("No block proposals provided")

        double_voters = self._detect_double_voters(blocks)

        # Score each block by valid votes after excluding double voters
        scored = []
        for b in blocks:
            votes = set(getattr(b, "votes", []))
            valid_votes = len([v for v in votes if v in self.validators and v not in double_voters])
            scored.append((b, valid_votes))

        required = max(1, math.ceil(len(self.validators) * self.quorum_fraction))
        candidates = [(b, v) for (b, v) in scored if v >= required]

        if not candidates:
            # No proposal reached quorum after excluding double voters
            raise RuntimeError(f"No block reached quorum after excluding double voters: {double_voters}")

        # Choose best candidate (highest valid votes, tie-breaker: first found)
        chosen = max(candidates, key=lambda x: x[1])[0]
        chosen.double_voters = double_voters
        return chosen
