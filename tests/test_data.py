import pytest
from binom_misprice.data import fetch_option_chain

@pytest.mark.parametrize("symbol,expiry", [
    ("AAPL", "2025-05-16"),
    ("MSFT", "2025-06-20"),
])
def test_fetch_option_chain_integration(symbol, expiry):
    # Integration test: requires internet. Will raise ValueError if ticker/expiry invalid.
    chain, spot = fetch_option_chain(symbol, expiry)
    assert hasattr(chain, "calls") and hasattr(chain, "puts")
    assert isinstance(spot, float) and spot > 0

def test_fetch_option_chain_invalid_symbol():
    with pytest.raises(ValueError):
        fetch_option_chain("NOTATICKER", "2025-05-16")

def test_fetch_option_chain_bad_date():
    with pytest.raises(ValueError):
        fetch_option_chain("AAPL", "bad-date")