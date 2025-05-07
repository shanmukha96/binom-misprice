import numpy as np
import pytest
from binom_misprice.tree import binomial_tree_price
from binom_misprice.bs import black_scholes_price

@pytest.mark.parametrize("opt_type", ['c', 'p'])
def test_binomial_vs_bs_european(opt_type):
    # European option: american=False should approximate Black-Scholes for many steps
    S, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.2
    # Use a 50-step tree for reasonable accuracy
    price_tree = binomial_tree_price(S, [K], T, r, sigma, steps=50, opt_type=opt_type, american=False)[0]
    price_bs = black_scholes_price(S, K, T, r, sigma, option_type=opt_type)
    assert abs(price_tree - price_bs) < 1e-2

def test_binomial_american_call_exercise():
    # American call on non-dividend stock should equal European price
    S, K, T, r, sigma = 100.0, 100.0, 0.5, 0.03, 0.25
    eu = binomial_tree_price(S, [K], T, r, sigma, steps=10, opt_type='c', american=False)[0]
    am = binomial_tree_price(S, [K], T, r, sigma, steps=10, opt_type='c', american=True)[0]
    assert pytest.approx(am, rel=1e-6) == eu
