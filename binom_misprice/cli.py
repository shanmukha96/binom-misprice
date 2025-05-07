#!/usr/bin/env python3

import sys
import argparse
import warnings
from .factor    import compute_call_mispricing, compute_put_mispricing
from .composite import compute_composite_mispricing, compute_mispricing_range
from .parallel  import compute_mispricing_batch

def main():
    parser = argparse.ArgumentParser(
        prog="binom-misprice",
        description="Compute option mispricing via binomial tree & Black‑Scholes"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- call ---
    p = sub.add_parser("call", help="Compute call mispricing")
    p.add_argument("--symbol",         required=True, help="Ticker symbol, e.g. AAPL")
    p.add_argument("--expiry",         required=True, help="Expiry YYYY-MM-DD")
    p.add_argument("--sigma",          type=float, help="Flat vol override")
    p.add_argument("--r",              type=float, default=0.03, help="Risk-free rate")
    p.add_argument("--steps",          type=int,   default=2,    help="Binomial steps")
    p.add_argument("--american",       action="store_true",     help="Allow early exercise")
    p.add_argument("--valuation_date", help="Valuation date YYYY-MM-DD")
    p.add_argument("--output",         help="CSV output path")

    # --- put ---
    p = sub.add_parser("put", help="Compute put mispricing")
    p.add_argument("--symbol",         required=True)
    p.add_argument("--expiry",         required=True)
    p.add_argument("--sigma",          type=float)
    p.add_argument("--r",              type=float, default=0.03)
    p.add_argument("--steps",          type=int,   default=2)
    p.add_argument("--american",       action="store_true")
    p.add_argument("--valuation_date", help="YYYY-MM-DD")
    p.add_argument("--output",         help="CSV output path")

    # --- composite ---
    p = sub.add_parser("composite", help="Compute call+put composite mispricing")
    p.add_argument("--symbol",         required=True)
    p.add_argument("--expiry",         required=True)
    p.add_argument("--w_call",         type=float, default=0.5, help="Weight on call")
    p.add_argument("--w_put",          type=float, default=0.5, help="Weight on put")
    p.add_argument("--sigma",          type=float)
    p.add_argument("--r",              type=float, default=0.03)
    p.add_argument("--steps",          type=int,   default=2)
    p.add_argument("--american",       action="store_true")
    p.add_argument("--valuation_date", help="YYYY-MM-DD")
    p.add_argument("--output",         help="CSV output path")

    # --- range ---
    p = sub.add_parser("range", help="Compute mispricing over a date range")
    p.add_argument("--symbol",    required=True)
    p.add_argument("--expiry",    required=True)
    p.add_argument("--start_date",required=True, help="Start YYYY-MM-DD")
    p.add_argument("--end_date",  required=True, help="End   YYYY-MM-DD")
    p.add_argument("--factor",    choices=["call","put","composite"], default="composite")
    p.add_argument("--w_call",    type=float, default=0.5)
    p.add_argument("--w_put",     type=float, default=0.5)
    p.add_argument("--sigma",     type=float)
    p.add_argument("--r",         type=float, default=0.03)
    p.add_argument("--steps",     type=int,   default=2)
    p.add_argument("--american",  action="store_true")
    p.add_argument("--output",    help="CSV output path")

    # --- batch ---
    p = sub.add_parser("batch", help="Compute mispricing for multiple tickers in parallel")
    p.add_argument("--tickers",     required=True, help="Comma-separated list e.g. AAPL,MSFT")
    p.add_argument("--expiry",      required=True)
    p.add_argument("--start_date",  required=True)
    p.add_argument("--end_date",    required=True)
    p.add_argument("--factor",      choices=["call","put","composite"], default="composite")
    p.add_argument("--w_call",      type=float, default=0.5)
    p.add_argument("--w_put",       type=float, default=0.5)
    p.add_argument("--sigma",       type=float)
    p.add_argument("--r",           type=float, default=0.03)
    p.add_argument("--steps",       type=int,   default=2)
    p.add_argument("--american",    action="store_true")
    p.add_argument("--max_workers", type=int,   default=4)
    p.add_argument("--output",      help="CSV output path")

    args = parser.parse_args()

    try:
        if args.command == "call":
            df = compute_call_mispricing(
                args.symbol, args.expiry,
                sigma=args.sigma,
                r=args.r,
                steps=args.steps,
                american=args.american,
                valuation_date=args.valuation_date
            )

        elif args.command == "put":
            df = compute_put_mispricing(
                args.symbol, args.expiry,
                sigma=args.sigma,
                r=args.r,
                steps=args.steps,
                american=args.american,
                valuation_date=args.valuation_date
            )

        elif args.command == "composite":
            df = compute_composite_mispricing(
                args.symbol, args.expiry,
                sigma=args.sigma,
                r=args.r,
                steps=args.steps,
                american=args.american,
                w_call=args.w_call,
                w_put=args.w_put,
                valuation_date=args.valuation_date
            )

        elif args.command == "range":
            df = compute_mispricing_range(
                args.symbol, args.expiry,
                args.start_date, args.end_date,
                factor=args.factor,
                sigma=args.sigma,
                r=args.r,
                steps=args.steps,
                american=args.american,
                w_call=args.w_call,
                w_put=args.w_put
            )

        elif args.command == "batch":
            tickers = [t.strip() for t in args.tickers.split(",")]
            df = compute_mispricing_batch(
                tickers,
                args.expiry,
                args.start_date,
                args.end_date,
                factor=args.factor,
                sigma=args.sigma,
                r=args.r,
                steps=args.steps,
                american=args.american,
                w_call=args.w_call,
                w_put=args.w_put,
                max_workers=args.max_workers
            )

        else:
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # output
    if args.output:
        df.to_csv(args.output, index=False)
        print(f"Saved results to {args.output}")
    else:
        print(df.to_string(index=False))


if __name__ == "__main__":
    main()
