import pytest
from binom_misprice.factor import compute_call_mispricing, compute_put_mispricing

@pytest.mark.parametrize("opt_func", [compute_call_mispricing, compute_put_mispricing])
def test_compute_mispricing_columns(opt_func):
    df = opt_func("AAPL", "2025-05-16", steps=2)
    # Should have exactly these columns
    assert set(df.columns) == {"strike", "market_price", "theo_price", "mispricing"}
    # Should not be empty for liquid tickers
    assert not df.empty

def test_expired_option_error():
    # expiry in the past relative to today
    with pytest.raises(ValueError):
        compute_call_mispricing("AAPL", "2000-01-01", steps=2)