import pytest
from binom_misprice.composite import compute_composite_mispricing, compute_mispricing_range

def test_composite_weights():
    # Valid weights
    df = compute_composite_mispricing("AAPL", "2025-05-16", w_call=0.7, w_put=0.3, steps=2)
    assert set(df.columns) == {"strike", "mispricing"}

    # Invalid weights should raise
    with pytest.raises(ValueError):
        compute_composite_mispricing("AAPL", "2025-05-16", w_call=1.1, w_put=-0.1, steps=2)

def test_range_factor_selection():
    # Only one day range
    df = compute_mispricing_range("AAPL", "2025-05-16", "2025-05-15", "2025-05-15", factor="call", steps=2)
    assert "valuation_date" in df.columns
    assert not df.empty