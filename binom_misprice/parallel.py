import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from .composite import compute_mispricing_range

def _mispricing_worker(
    symbol, expiry, start_date, end_date,
    factor, sigma, r, steps, american, w_call, w_put
):
    try:
        df = compute_mispricing_range(
            symbol=symbol,
            expiry=expiry,
            start_date=start_date,
            end_date=end_date,
            factor=factor,
            sigma=sigma,
            r=r,
            steps=steps,
            american=american,
            w_call=w_call,
            w_put=w_put
        )
        df["symbol"] = symbol
        return df
    except Exception:
        return None

def compute_mispricing_batch(
    tickers,
    expiry,
    start_date,
    end_date,
    factor: str = "composite",
    sigma: float = None,
    r: float = 0.03,
    steps: int = 2,
    american: bool = False,
    w_call: float = 0.5,
    w_put: float = 0.5,
    output_path: str = None,
    max_workers: int = 4
) -> pd.DataFrame:
    if not isinstance(tickers, (list, tuple)):
        raise ValueError("tickers must be a list or tuple of symbols")

    futures = []
    with ProcessPoolExecutor(max_workers=max_workers) as exec:
        for sym in tickers:
            futures.append(
                exec.submit(
                    _mispricing_worker,
                    sym, expiry, start_date, end_date,
                    factor, sigma, r, steps, american, w_call, w_put
                )
            )
    results = [f.result() for f in futures if f.result() is not None]

    if not results:
        raise ValueError("No data returned for any tickers")
    combined = pd.concat(results, ignore_index=True)
    if output_path:
        combined.to_csv(output_path, index=False)
    return combined
