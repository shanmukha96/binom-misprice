import pandas as pd
import yfinance as yf

# 1) Load your existing filtered file
df = pd.read_csv("mispricing_Q1_2025_with_yields.csv")

# 2) Convert valuation_date to datetime
df["valuation_date"] = pd.to_datetime(df["valuation_date"])

# 3) Re-apply the 90–110% band
cleaned = []
for sym, sub in df.groupby("symbol"):
    # use the first valuation_date to fetch current spot
    spot = yf.Ticker(sym).history(period="1d")["Close"][-1]
    lo, hi = 0.9 * spot, 1.1 * spot

    # filter on strike
    sub2 = sub[(sub["strike"] >= lo) & (sub["strike"] <= hi)]
    if sub2.empty:
        print(f"⚠️  {sym}: no strikes in 90–110% band, skipping")
    else:
        cleaned.append(sub2)

# 4) Combine and save
if not cleaned:
    raise RuntimeError("No data remains after re-filtering!")
df_clean = pd.concat(cleaned, ignore_index=True)
df_clean.to_csv("mispricing_Q1_2025_90_110_refined.csv", index=False)
print(f"Saved refined CSV with {len(df_clean)} rows as mispricing_Q1_2025_90_110_refined.csv")
