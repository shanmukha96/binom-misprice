#!/usr/bin/env python

import pandas as pd

from binom_misprice import (
    fetch_option_chain,
    compute_call_mispricing,
    compute_put_mispricing,
    compute_composite_mispricing,
    compute_mispricing_range,
    compute_mispricing_batch,
)

def main():
    # 1. Raw option chain + spot
    symbol = "AAPL"
    expiry = "2025-05-16"

    chain, spot = fetch_option_chain(symbol, expiry)
    print(f"\n=== Raw Option Chain for {symbol} expiring {expiry} ===")
    print(chain.calls.head(), "\n")
    print("Underlying spot price used:", spot, "\n")

    # 2. Single-date mispricing for calls and puts
    print("=== Single-date Call Mispricing ===")
    df_call = compute_call_mispricing(
        symbol=symbol, expiry=expiry,
        steps=2, american=True
    )
    print(df_call.head(), "\n")
    df_call.to_csv(f"{symbol}_call_mispricing_{expiry}.csv", index=False)

    print("=== Single-date Put Mispricing ===")
    df_put = compute_put_mispricing(
        symbol=symbol, expiry=expiry,
        steps=2, american=True
    )
    print(df_put.head(), "\n")
    df_put.to_csv(f"{symbol}_put_mispricing_{expiry}.csv", index=False)

    # 3. Composite mispricing on a date range
    print("=== Composite Mispricing Over a Date Range ===")
    df_comp_range = compute_mispricing_range(
        symbol=symbol,
        expiry=expiry,
        start_date="2025-04-20",
        end_date="2025-04-25",
        factor="composite",
        steps=2,
        american=True,
        w_call=0.6,
        w_put=0.4,
        output_path=f"{symbol}_composite_mispricing_{expiry}_range.csv"
    )
    print(df_comp_range.head(), "\n")

    # 4. Parallel batch across multiple tickers
    print("=== Parallel Batch Mispricing for Multiple Symbols ===")
    symbols = ["AAPL", "MSFT", "GOOG"]
    df_batch = compute_mispricing_batch(
        tickers=symbols,
        expiry=expiry,
        start_date="2025-04-20",
        end_date="2025-04-20",
        factor="call",
        steps=2,
        american=True,
        max_workers=4,
        output_path="batch_call_mispricing.csv"
    )
    print(df_batch.head(), "\n")

    # 5. Save combined results
    df_batch.to_csv("batch_call_mispricing.csv", index=False)
    print("Saved all CSVs to disk.")

if __name__ == "__main__":
    main()
