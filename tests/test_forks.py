import pytest
from blockchain.consensus import FederatedConsensus
from blockchain.chain import TriChain

def test_conflict_resolution_prefers_quorum():
    validators = [f"v{i}" for i in range(1, 6)]  # v1..v5
    c = FederatedConsensus(validators, quorum_fraction=0.51)  # needs 3 of 5
    chain = TriChain(validators)

    # Two conflicting proposals: A gets 3 votes, B gets 2 votes
    split_votes = [["v1", "v2", "v3"], ["v4", "v5"]]
    proposals = c.propose_conflicting(chain.chain, [], split_votes)

    chosen = chain.resolve_and_append(proposals)

    assert len(chain.chain) == 2
    assert set(chosen.votes) >= {"v1", "v2", "v3"}

def test_double_voting_detection_causes_rejection():
    validators = [f"v{i}" for i in range(1, 6)]  # v1..v5
    # make quorum 60% -> 3 of 5 required
    c = FederatedConsensus(validators, quorum_fraction=0.6)
    chain = TriChain(validators)

    # v1 double-votes (appears in both proposals). After excluding double-voter,
    # neither proposal reaches the 3-vote quorum and resolution must fail.
    split_votes = [["v1", "v2", "v3"], ["v1", "v4", "v5"]]
    proposals = c.propose_conflicting(chain.chain, [], split_votes)

    with pytest.raises(RuntimeError):
        chain.resolve_and_append(proposals)
