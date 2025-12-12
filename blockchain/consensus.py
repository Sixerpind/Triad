from .block import Block

class FederatedConsensus:
    """Simple federated consensus with quorum voting simulation.

    This prototype simulates validator votes and attaches a "votes" list to
    blocks. A block is considered accepted if the number of validator votes
    meets or exceeds the quorum (default >50%). For real-world usage, replace
    the simulation with cryptographic signatures and network messaging.
    """

    def __init__(self, validators, quorum_fraction=0.51):
        if not validators:
            raise ValueError("validators list must not be empty")
        self.validators = list(validators)
        # quorum_fraction is fraction of validators required to accept a block
        self.quorum_fraction = float(quorum_fraction)

    def _simulate_votes(self):
        """Simulate votes from all validators. In a real implementation this
        would collect signed votes over the network."""
        # For prototype, every validator votes for the proposed block
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
        # attach validator votes to block metadata
        new_block.votes = votes
        return new_block

    def validate_votes(self, block):
        """Validate that the block has enough votes to reach quorum."""
        if not hasattr(block, "votes"):
            return False
        votes = set(block.votes)
        # count only votes from known validators
        valid_votes = len([v for v in votes if v in self.validators])
        required = max(1, int(len(self.validators) * self.quorum_fraction))
        return valid_votes >= required
