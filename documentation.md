Here’s an expanded **documentation.md** with detailed parameter lists (and `null`/`None` allowed to use defaults) for each Python API function. Copy this entire block into your `documentation.md`.

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

# or install editable from source (including dev extras)
git clone https://github.com/shanmukha96/binom-misprice.git
cd binom_misprice
pip install -e .[dev]
````

### R

```r
# 1. Install reticulate & dplyr
install.packages(c("reticulate","dplyr"))

# 2. Create an R virtualenv and install Python package into it
reticulate::virtualenv_create("binom_misprice_env", python = "python3")
reticulate::virtualenv_install("binom_misprice_env", packages = "binom_misprice", pip = TRUE)
```

---

## 3. Python API

Import the package:

```python
import binom_misprice as bm
```

### 3.1 Pricing Primitives

#### `binomial_tree_price`

```python
bm.binomial_tree_price(
    S: float,
    strikes: List[float],
    T: float,
    r: float,
    sigma: Optional[float] = None,
    steps: int = 50,
    opt_type: str = 'c',
    american: bool = True,
    q: float = 0.0
) -> pd.DataFrame
```

* **S** (`float`): Underlying spot price.
* **strikes** (`List[float]`): One or more strike prices.
* **T** (`float`): Time to expiry in years.
* **r** (`float`): Continuously‑compounded risk‑free rate.
* **sigma** (`float` or `None`): Volatility.

  * `None` (default): fetch per‑strike IV; fallback to 60‑day hist‑vol if missing.
  * `>0`: override all strikes with this flat volatility.
* **steps** (`int`): Number of binomial steps (higher → smoother tree).
* **opt\_type** (`'c'` or `'p'`): `'c'`=call, `'p'`=put.
* **american** (`bool`): Early‑exercise enabled if `True`.
* **q** (`float`): Continuous dividend yield.

Returns a DataFrame indexed by strike (and date if vectorized) of theoretical prices.

#### `black_scholes_price`

```python
bm.black_scholes_price(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: Optional[float] = None,
    option_type: str = 'c',
    q: float = 0.0
) -> float
```

* **S** (`float`): Spot price.
* **K** (`float`): Strike price.
* **T** (`float`): Time to expiry in years.
* **r** (`float`): Risk‑free rate.
* **sigma** (`float` or `None`): Volatility (same logic as above).
* **option\_type** (`'c'` or `'p'`): Call or put.
* **q** (`float`): Dividend yield.

Returns a single Black–Scholes price (European only).

---

### 3.2 Mispricing Factors

#### `compute_call_mispricing`

```python
bm.compute_call_mispricing(
    symbol: str,
    expiry: str,
    sigma: Optional[float] = None,
    r: float = 0.0,
    steps: int = 50,
    american: bool = True,
    implied_vols: Optional[Sequence[float]] = None,
    valuation_date: Optional[str] = None
) -> pd.DataFrame
```

* **symbol** (`str`): Ticker symbol (e.g. `"AAPL"`).
* **expiry** (`str`): Expiry date `"YYYY-MM-DD"`.
* **sigma** (`float` or `None`): Flat vol override; `None` triggers IV fetch + fallback.
* **r** (`float`): Risk‑free rate.
* **steps** (`int`): Binomial steps.
* **american** (`bool`): Early‑exercise if `True`.
* **implied\_vols** (`Sequence[float]` or `None`): User‑supplied IV array (highest precedence).
* **valuation\_date** (`str` or `None`): Pricing date (`None` = today).

Returns per‑strike call mispricing DataFrame.

#### `compute_put_mispricing`

```python
# Same signature as compute_call_mispricing
bm.compute_put_mispricing(...)
```

Identical parameters but computes put mispricing.

#### `compute_composite_mispricing`

```python
bm.compute_composite_mispricing(
    symbol: str,
    expiry: str,
    w_call: float,
    w_put: float,
    sigma: Optional[float] = None,
    r: float = 0.0,
    steps: int = 50,
    american: bool = True,
    implied_vols: Optional[Sequence[float]] = None,
    valuation_date: Optional[str] = None
) -> pd.DataFrame
```

* **w\_call**, **w\_put** (`float`): Weights for call and put mispricing (sum to 1).
  Other params as above.

---

### 3.3 Date‑Range Scanning

#### `compute_mispricing_range`

```python
bm.compute_mispricing_range(
    symbol: str,
    expiry: str,
    start_date: str,
    end_date: str,
    factor: str = 'call',
    sigma: Optional[float] = None,
    r: float = 0.0,
    steps: int = 50,
    american: bool = True,
    implied_vols: Optional[Sequence[float]] = None,
    output_path: Optional[str] = None
) -> pd.DataFrame
```

* **start\_date**, **end\_date** (`str`): `"YYYY-MM-DD"` range.
* **factor** (`'call'`, `'put'`, `'composite'`).
* **output\_path** (`str` or `None`): CSV file to save results.

---

### 3.4 Parallel Batch Processing

#### `compute_mispricing_batch`

```python
bm.compute_mispricing_batch(
    tickers: Sequence[str],
    expiry: str,
    start_date: str,
    end_date: str,
    factor: str = 'call',
    sigma: Optional[float] = None,
    r: float = 0.0,
    steps: int = 50,
    american: bool = True,
    implied_vols: Optional[Sequence[float]] = None,
    max_workers: int = 4,
    output_path: Optional[str] = None
) -> pd.DataFrame
```

* **tickers** (`Sequence[str]`): List of symbols.
* **max\_workers** (`int`): Threads for parallel execution.

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

All the same Python‑API parameters can be passed as flags; omit any to let the system choose defaults.

---

## 5. R API (via reticulate)

```r
library(reticulate)
use_virtualenv("binom_env", required = TRUE)
library(binommisprice)

# Call mispricing
dfc <- compute_call_mispricing(
  symbol = "AAPL",
  expiry = "2025-12-19",
  steps = 2L,
  american = TRUE,
  sigma = NULL         # letting Python fetch IV + fallback
)
```

---

## 6. Notes & Tips

* **Passing `None`/`null`**
  Any parameter marked optional can be set to `None` (Python) or `NULL` (R) to invoke built‑in defaults—e.g. fetching IVs or using today’s date.

* **Volatility Input**

  1. `implied_vols` array overrides everything
  2. `sigma=float` sets flat vol
  3. `sigma=None` → per‑strike IV + 60‑day hist‑vol fallback

* **Error Handling & Warnings**

  * Missing IV → single warning listing strikes using historical vol.
  * Invalid inputs → `ValueError` / `stop()`

* **Performance**

  * Increase `steps` for smoother trees.
  * Use `max_workers` for faster multi‑ticker runs

---
