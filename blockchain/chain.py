from .transaction import Transaction
from .block import Block
from .consensus import FederatedConsensus
from .poh import ProofOfHistory
from .executor import ParallelExecutor

class TriChain:
    def __init__(self, validators):
        self.chain = []
        self.current_transactions = []
        self.validators = validators
        self.consensus = FederatedConsensus(validators)
        self.poh = ProofOfHistory()
        self.executor = ParallelExecutor()

        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(0, [], "0")
        self.chain.append(genesis)

    def add_transaction(self, sender, receiver, amount):
        tx = Transaction(sender, receiver, amount)
        self.current_transactions.append(tx)
        return tx

    def create_micro_block(self):
        """
        Propose a single micro block via federated consensus and append only if quorum is reached.
        """
        block = self.consensus.vote(self.chain, self.current_transactions)
        if self.consensus.validate_votes(block):
            self.current_transactions = []
            self.chain.append(block)
            return block
        else:
            raise RuntimeError("Consensus quorum not reached; block rejected")

    def create_pow_checkpoint(self, difficulty=4):
        last = self.chain[-1]
        checkpoint = Block(len(self.chain), [], last.hash, pow_checkpoint=True)
        checkpoint.proof_of_work(difficulty)
        self.chain.append(checkpoint)
        return checkpoint

    def run_parallel(self, tasks):
        return self.executor.execute(tasks)

    def poh_event(self):
        return self.poh.record_event()

    def resolve_and_append(self, proposals):
        """
        Given multiple conflicting proposals (list of Block objects), resolve the conflict
        using the consensus module and append the chosen block to the chain.

        Fork handling:
        - If the chosen block's prev_hash matches the current head, append normally.
        - If the chosen block references an earlier height, truncate the chain to that parent and
          append the chosen block (simple fork switch).
        - If the chosen block's parent is unknown, error.

        Returns the block appended.
        """
        chosen = self.consensus.resolve_conflict(proposals)

        # Find parent in current chain
        parent_index = None
        for i, b in enumerate(self.chain):
            if b.hash == chosen.prev_hash:
                parent_index = i
                break

        if parent_index is None:
            raise RuntimeError("Chosen block references unknown parent; cannot attach")

        # Truncate chain to parent and append chosen block (simple fork switch)
        self.chain = self.chain[: parent_index + 1]
        self.chain.append(chosen)

        # Clear current_transactions on success. In a realistic implementation we'd
        # reconcile orphaned transactions and re-inject them appropriately.
        self.current_transactions = []

        return chosen
