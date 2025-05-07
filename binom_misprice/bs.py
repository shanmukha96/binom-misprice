# Updated binom_misprice/bs.py with dividend yield support

from math import log, sqrt, exp, erf

def black_scholes_price(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str = 'c',
    q: float = 0.0
) -> float:
    """
    Calculate the Black-Scholes price for a European option with continuous dividends.
    
    Parameters:
      - S: current underlying price
      - K: strike price
      - T: time to expiration in years
      - r: risk-free interest rate (annual, continuous compounding)
      - sigma: volatility of the underlying (annual standard deviation)
      - option_type: 'c' for call, 'p' for put
      - q: continuous dividend yield (as a decimal, e.g. 0.02 for 2%)
    
    Returns:
      - The theoretical price of the option (float).
    """

    # Input validation
    if S <= 0 or K <= 0:
        raise ValueError("Underlying price S and strike K must be positive")
    if T < 0:
        raise ValueError("Time to expiration T cannot be negative")
    if sigma < 0:
        raise ValueError("Volatility sigma must be non-negative")
    if option_type not in ('c', 'p'):
        raise ValueError("option_type must be 'c' for call or 'p' for put")
    if q < 0:
        raise ValueError("Dividend yield q must be non-negative")

    # If no time or no volatility, option value is its intrinsic (with discounting and dividends)
    if T == 0 or sigma == 0:
        if option_type == 'c':
            # Present value of forward payoff for a call
            return max(0.0, S * exp(-q * T) - K * exp(-r * T))
        else:
            # Present value of forward payoff for a put
            return max(0.0, K * exp(-r * T) - S * exp(-q * T))

    # Adjusted d1, d2 accounting for continuous dividend yield
    d1 = (log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    # Standard normal cumulative distribution via erf
    N = lambda x: 0.5 * (1.0 + erf(x / sqrt(2.0)))

    if option_type == 'c':
        # Call price with dividends
        return S * exp(-q * T) * N(d1) - K * exp(-r * T) * N(d2)
    else:
        # Put price with dividends
        return K * exp(-r * T) * N(-d2) - S * exp(-q * T) * N(-d1)

