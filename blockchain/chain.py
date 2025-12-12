from .transaction import Transaction
from .block import Block
from .consensus import FederatedConsensus
from .poh import ProofOfHistory
from .executor import ParallelExecutor
from typing import List, Callable, Any


class TriChain:
    def __init__(self, validators: List[str]):
        self.chain: List[Block] = []
        self.current_transactions: List[Transaction] = []
        self.validators = list(validators)
        self.consensus = FederatedConsensus(validators)
        self.poh = ProofOfHistory()
        self.executor = ParallelExecutor()

        self.create_genesis_block()

    def create_genesis_block(self) -> Block:
        genesis = Block(index=0, transactions=[], prev_hash="0", pow_checkpoint=False)
        # make sure genesis hash is computed
        genesis.compute_hash()
        self.chain.append(genesis)
        return genesis

    def add_transaction(self, sender: str, receiver: str, amount: float) -> Transaction:
        tx = Transaction(sender, receiver, amount)
        self.current_transactions.append(tx)
        return tx

    def create_micro_block(self) -> Block:
        """
        Propose a single micro block via federated consensus and append only if quorum is reached.
        """
        block = self.consensus.vote(self.chain, self.current_transactions)
        if self.consensus.validate_votes(block):
            # include transactions from the block (they were passed in by consensus)
            self.current_transactions = []
            self.chain.append(block)
            return block
        else:
            raise RuntimeError("Consensus quorum not reached; block rejected")

    def create_pow_checkpoint(self, difficulty: int = 4) -> Block:
        last = self.chain[-1]
        checkpoint = Block(index=len(self.chain), transactions=[], prev_hash=last.hash, pow_checkpoint=True)
        checkpoint.proof_of_work(difficulty)
        self.chain.append(checkpoint)
        return checkpoint

    def run_parallel(self, tasks: List[Callable[..., Any]]) -> List[Any]:
        """
        Execute tasks in parallel via the ParallelExecutor.
        Each task is a callable (no-arg or with args via lambda closure).
        Returns list of results matching task order.
        """
        return self.executor.execute(tasks)

    def poh_event(self) -> str:
        """
        Record an event in the Proof of History and return the resulting digest.
        """
        return self.poh.record_event()

    def resolve_and_append(self, proposals: List[Block]) -> Block:
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

        # Normalize chosen.prev_hash and block.hash as hex strings
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
