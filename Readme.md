# binom_misprice

**binom_misprice** is a Python library for detecting option mis‑pricing via vectorized binomial trees (American puts + optional American calls) and Black‑Scholes (European), with composite signals, date‑range scans and parallel batch processing.

## Installation
```bash
# From PyPI
pip install binom-misprice

# From the latest source
git clone https://github.com/shanmukha96/binom-misprice.git
cd binom_misprice
pip install -e .
````

## Quickstart
```python
import binom_misprice as bm
# simple call mispricing
df = bm.compute_call_mispricing(
    symbol="AAPL",
    expiry="2025-12-19",
    steps=3,
    american=True
)
print(df.head())
```
## CLI
```bash
binom-misprice call --symbol AAPL --expiry 2025-12-19 --steps 3 --american --output call.csv
```
Run `binom-misprice --help` for all subcommands.
## Documentation
Full API docs, examples, and the R interface are in **documentation.md** at the project root.
## License
Released under the **MIT License**. See [LICENSE](LICENSE) for details.
