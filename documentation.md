Thought for a couple of seconds


Below are the two complete markdown documents. Just copy each block into your `documentation.md` and `README.md` files respectively.

---

````markdown
# binom_misprice — Usage Documentation

This document covers installation, Python & R APIs, the CLI, and tips for **binom_misprice**.

---

## 1. Requirements

- **Python**: 3.8 or higher  
- **R**: (if using the R wrapper) 4.x  
- **Dependencies**: `numpy`, `pandas`, `yfinance`, plus `reticulate` & `dplyr` for R wrapper  

---

## 2. Installation

### Python

```bash
# 1. (Optional) Create & activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate    # Windows PowerShell: .venv\Scripts\Activate.ps1

# 2. Upgrade pip & packaging tools
pip install --upgrade pip setuptools wheel

# 3. Install from PyPI
pip install binom-misprice

# or install editable from source (including dev extras)
git clone https://github.com/youruser/binom_misprice.git
cd binom_misprice
pip install -e .[dev]
````

### R

```r
# 1. Install reticulate & dplyr
install.packages(c("reticulate","dplyr"))

# 2. Create an R virtualenv and install Python package into it
reticulate::virtualenv_create("binom_env", python = "python3")
reticulate::virtualenv_install("binom_env", packages = "binom-misprice", pip = TRUE)
```

---

## 3. Python API

Import the top‑level module:

```python
import binom_misprice as bm
```

### 3.1 Pricing Models

```python
# Binomial tree (American or European)
prices = bm.binomial_tree_price(
    S=100,
    strikes=[90,100,110],
    T=30/252,
    r=0.01,
    sigma=0.2,
    steps=3,
    opt_type='c',
    american=True
)

# Black‑Scholes (European, with dividends q=0.0 by default)
bs_price = bm.black_scholes_price(
    S=100,
    K=100,
    T=30/252,
    r=0.01,
    sigma=0.2,
    option_type='c'
)
```

### 3.2 Mispricing Factors

```python
# 1) Call mispricing for one expiry, default IV fetch & fallback
df_call = bm.compute_call_mispricing(
    symbol="AAPL",
    expiry="2025-12-19",
    steps=2,
    american=True
)

# 2) Put mispricing with flat sigma override (25%)
df_put = bm.compute_put_mispricing(
    symbol="AAPL",
    expiry="2025-12-19",
    sigma=0.25,
    steps=2,
    american=False
)

# 3) Call mispricing injecting your own per-strike IV array
my_ivs = [...]  # numpy array aligned to the strikes
df_call_iv = bm.compute_call_mispricing(
    symbol="AAPL",
    expiry="2025-12-19",
    steps=2,
    american=True,
    implied_vols=my_ivs
)

# 4) Composite mispricing (60% call + 40% put)
df_comp = bm.compute_composite_mispricing(
    symbol="AAPL",
    expiry="2025-12-19",
    w_call=0.6,
    w_put=0.4,
    steps=2,
    american=True
)
```

### 3.3 Date‐Range Scanning

```python
df_range = bm.compute_mispricing_range(
    symbol="AAPL",
    expiry="2025-12-19",
    start_date="2025-11-01",
    end_date="2025-11-05",
    factor="composite",     # 'call', 'put', or 'composite'
    steps=3,
    american=True,
    output_path="mispricing_range.csv"
)
```

### 3.4 Parallel Batch for Multiple Tickers

```python
symbols = ["AAPL","MSFT","GOOG"]
df_batch = bm.compute_mispricing_batch(
    tickers=symbols,
    expiry="2025-12-19",
    start_date="2025-11-01",
    end_date="2025-11-05",
    factor="call",
    steps=3,
    american=False,
    max_workers=4,
    output_path="batch_call_mispricing.csv"
)
```
# american and implied volatility
df = bm.compute_call_mispricing(
  symbol="AAPL", expiry="2025-12-19",
  steps=3, american=True,
  implied_vols=my_iv_array
)
---

## 4. Command‑Line Interface

If you installed the CLI extras, you can run:

```bash
binom-misprice \
  --symbol AAPL \
  --expiry 2025-12-19 \
  --factor composite \
  --steps 3 \
  --american \
  --output out.csv
```

---

## 5. R API (via reticulate)

```r
library(reticulate)
use_virtualenv("binom_env", required = TRUE)
library(binommisprice)    # or your R package name

# Call mispricing
dfc <- compute_call_mispricing(
  symbol = "AAPL",
  expiry = "2025-12-19",
  steps = 2L,
  american = TRUE
)

# Put mispricing with sigma override
dfp <- compute_put_mispricing(
  symbol = "AAPL",
  expiry = "2025-12-19",
  sigma = 0.25,
  steps = 2L,
  american = FALSE
)

# Composite mispricing
dfcomp <- compute_composite_mispricing(
  symbol = "AAPL",
  expiry = "2025-12-19",
  w_call = 0.6,
  w_put  = 0.4,
  steps  = 2L,
  american= TRUE
)
```

---

## 6. Notes & Tips

* **American vs European**

  * Set `american=True` for early‑exercise in binomial trees.
  * `black_scholes_price()` is always European.

* **Volatility Input**

  * `sigma=None` (default) → per‑strike IV from `yfinance`, fallback to 60‑day historical vol.
  * `sigma=<float>` → override all strikes.
  * `implied_vols=<array>` → user‑supplied per‑strike array (takes highest precedence).

* **IV Fallbacks**

  * If `yfinance`’s implied‑vol column is missing or zero, you’ll get a single `UserWarning` listing the affected strikes and the 60‑day hist‑vol used instead.

* **Error Handling**

  * Invalid symbol or expiry → `ValueError` (Python) / `stop()` (R).
  * Empty chains, expired options, or non‑positive theoretical prices are filtered or error out gracefully.

* **Performance**

  * Vectorized pricing over strikes & parallel batch processing for multi‑ticker scans.
  * Example caching shown in docs (via `functools.lru_cache`) to reduce repeated data requests.

---

*End of documentation.md*

````

---

```markdown
# binom_misprice

[![PyPI version](https://badge.fury.io/py/binom-misprice.svg)](https://pypi.org/project/binom-misprice/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Build Status](https://github.com/youruser/binom_misprice/actions/workflows/ci.yml/badge.svg)](https://github.com/youruser/binom_misprice/actions)

**binom_misprice** is a production‑grade Python package for detecting option mispricing using:
- **Binomial‑tree** (CRR) pricer with **American**‑put support  
- **Black‑Scholes** analytic pricer with continuous dividends  
- **Per‑strike implied‑vol** integration (with 60‑day hist‑vol fallback & warnings)  
- **Composite signals**, **date‑range scans**, **parallel batch** processing  
- **R interface** via **reticulate** and optional **CLI**  

---

## Installation

```bash
# Latest from PyPI
pip install binom-misprice

# from source (with dev/test extras)
git clone https://github.com/youruser/binom_misprice.git
cd binom_misprice
pip install -e .[dev]
````

---

## Quickstart

```python
import binom_misprice as bm

# Compute call mispricing for AAPL expiring 2025‑12‑19 using 3‑step American tree
df = bm.compute_call_mispricing(
    symbol="AAPL",
    expiry="2025-12-19",
    steps=3,
    american=True
)

print(df.head())
```

---

## Core API

```python
# Pricing
bm.binomial_tree_price(S, strikes, T, r, sigma, steps, opt_type, american, q)
bm.black_scholes_price(S, K, T, r, sigma, option_type, q)

# Mispricing Factors
bm.compute_call_mispricing(symbol, expiry, sigma=None, r=0.03,
                           steps=2, american=False, implied_vols=None)

bm.compute_put_mispricing(...)

bm.compute_composite_mispricing(...)

# Range & Batch
bm.compute_mispricing_range(...)
bm.compute_mispricing_batch(...)
```

---

## Command‑Line Interface

```bash
binom-misprice --symbol AAPL \
               --expiry 2025-12-19 \
               --factor composite \
               --steps 3 \
               --american \
               --output mispricings.csv
```

---

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

---

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/foo`)
3. Commit your changes (`git commit -am 'Add foo'`)
4. Push to the branch (`git push origin feature/foo`)
5. Open a Pull Request

Please ensure all tests pass (`pytest`) and follow PEP 8 styling.

