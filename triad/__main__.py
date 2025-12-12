import argparse
import json
import sys
from blockchain.chain import TriChain

DEFAULT_VALIDATORS = ["v1", "v2", "v3"]


def main(argv=None):
    parser = argparse.ArgumentParser(prog="triad", description="Triad CLI (trichain demo)")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("status", help="Print basic chain status")
    add_tx = sub.add_parser("tx", help="Create a transaction")
    add_tx.add_argument("--from", dest="sender", required=True)
    add_tx.add_argument("--to", dest="receiver", required=True)
    add_tx.add_argument("--amount", dest="amount", type=float, required=True)

    sub.add_parser("micro", help="Create a micro block via consensus")
    sub.add_parser("pow", help="Create a proof-of-work checkpoint")
    sub.add_parser("poh", help="Record and print a PoH event")

    args = parser.parse_args(argv)

    chain = TriChain(DEFAULT_VALIDATORS)

    if args.cmd == "status":
        print(json.dumps({"height": len(chain.chain), "head": chain.chain[-1].hash}, indent=2))
        return 0

    if args.cmd == "tx":
        tx = chain.add_transaction(args.sender, args.receiver, args.amount)
        print(json.dumps(tx.to_dict(), indent=2))
        return 0

    if args.cmd == "micro":
        blk = chain.create_micro_block()
        print(json.dumps(blk.to_dict(), indent=2))
        return 0

    if args.cmd == "pow":
        blk = chain.create_pow_checkpoint(difficulty=3)
        print(json.dumps(blk.to_dict(), indent=2))
        return 0

    if args.cmd == "poh":
        d = chain.poh_event()
        print(d)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
