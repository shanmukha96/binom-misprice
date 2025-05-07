import pytest
from math import exp, log, sqrt
from binom_misprice.bs import black_scholes_price

def test_bs_call_put_parity():
    S, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.2
    c = black_scholes_price(S, K, T, r, sigma, option_type='c')
    p = black_scholes_price(S, K, T, r, sigma, option_type='p')
    # c - p should equal discounted forward value S - K e^{-rT}
    assert pytest.approx(c - p, rel=1e-6) == (S - K * exp(-r * T))

def test_bs_zero_volatility():
    S, K, T, r, sigma = 100.0, 105.0, 0.5, 0.03, 0.0
    # With zero vol, price is intrinsic discounted for time value
    call = black_scholes_price(S, K, T, r, sigma, option_type='c')
    assert pytest.approx(call, rel=1e-6) == max(0.0, S - K * exp(-r * T))
    put = black_scholes_price(S, K, T, r, sigma, option_type='p')
    assert pytest.approx(put, rel=1e-6) == max(0.0, K * exp(-r * T) - S)
