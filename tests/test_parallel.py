
import pytest
from binom_misprice.parallel import compute_mispricing_batch

def test_parallel_single_ticker():
    df = compute_mispricing_batch(
        tickers=["AAPL"],
        expiry="2025-05-16",
        start_date="2025-05-15",
        end_date="2025-05-15",
        factor="call",
        steps=2,
        max_workers=2
    )
    assert "symbol" in df.columns
    # Only one symbol in column
    assert set(df["symbol"]) == {"AAPL"}
    assert not df.empty

def test_parallel_invalid_tickers():
    with pytest.raises(ValueError):
        compute_mispricing_batch(
            tickers="AAPL",  # not a list
            expiry="2025-05-16",
            start_date="2025-05-15",
            end_date="2025-05-15"
        )
