import unittest
from blockchain.chain import TriChain
from blockchain.transaction import Transaction

class TestTriChain(unittest.TestCase):
    def setUp(self):
        self.validators = ["a", "b", "c"]
        self.chain = TriChain(self.validators)

    def test_genesis(self):
        self.assertEqual(len(self.chain.chain), 1)
        self.assertIsNotNone(self.chain.chain[0].hash)

    def test_add_transaction_and_microblock(self):
        self.chain.add_transaction("alice", "bob", 1.23)
        self.assertEqual(len(self.chain.current_transactions), 1)
        blk = self.chain.create_micro_block()
        # after creating micro block, current transactions cleared and block appended
        self.assertEqual(len(self.chain.current_transactions), 0)
        self.assertEqual(self.chain.chain[-1], blk)

    def test_pow_checkpoint(self):
        chk = self.chain.create_pow_checkpoint(difficulty=2)
        self.assertTrue(chk.hash.startswith("0" * 2))

    def test_poh_event(self):
        d1 = self.chain.poh_event()
        d2 = self.chain.poh_event()
        self.assertNotEqual(d1, d2)

if __name__ == "__main__":
    unittest.main()
