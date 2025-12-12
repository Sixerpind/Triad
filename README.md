```markdown
# Triad (Trichain) — Python Implementation

This repository contains a small, portable Python implementation of the TriChain (trichain) example:
- blockchain core (blocks, transactions)
- a simple federated consensus simulator
- proof-of-history event recorder
- a small parallel executor
- packaging and tests

Requirements:
- Python 3.8+

Quickstart:
- Install the package locally in editable mode:
  python -m pip install -e .

- Run the CLI:
  python -m triad --help

- Run tests:
  python -m pytest

Packaging:
- A pyproject.toml file is included — use build tools (pip, build) to build a wheel or sdist.

This implementation targets cross-platform compatibility (macOS, Windows 10/11) and uses only Python standard library modules.
```
