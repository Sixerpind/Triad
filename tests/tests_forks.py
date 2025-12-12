import pytest
from blockchain.block import Block
from blockchain.consensus import FederatedConsensus
from blockchain.chain import TriChain


def test_fork_switch_to_earlier_parent():
    validators = [f"v{i}" for i in range(1, 6)]
    chain = TriChain(validators)

    # Append a micro block so the head is no longer genesis
    chain.create_micro_block()
    assert len(chain.chain) == 2

    # Manually craft proposals that reference genesis (earlier parent)
    genesis = chain.chain[0]
    # Proposal A has quorum of 3 votes
    a = Block(index=1, transactions=[], prev_hash=genesis.hash)
    a.votes = ["v1", "v2", "v3"]

    # Proposal B has fewer votes
    b = Block(index=1, transactions=[], prev_hash=genesis.hash)
    b.votes = ["v4"]

    proposals = [a, b]
    chosen = chain.resolve_and_append(proposals)

    # Chain should be truncated to genesis + chosen
    assert len(chain.chain) == 2
    assert chain.chain[-1] is chosen
    assert chain.chain[-1].prev_hash == genesis.hash


def test_unknown_parent_raises():
    validators = [f"v{i}" for i in range(1, 6)]
    chain = TriChain(validators)

    # Create a proposal referencing an unknown parent
    p = Block(index=1, transactions=[], prev_hash="deadbeef")
    p.votes = ["v1", "v2", "v3"]

    with pytest.raises(RuntimeError):
        chain.resolve_and_append([p])
