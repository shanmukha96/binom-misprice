import numpy as np
from .bs import black_scholes_price

def binomial_tree_price(
    S,
    strikes,
    T,
    r,
    sigma,
    steps: int = 2,
    opt_type: str = "c",
    american: bool = False,
    q: float = 0.0
):
    """
    Vectorized option pricer:
      - If american=False or opt_type=='c': falls back to Black‑Scholes with dividend q.
      - If american=True and opt_type=='p': uses CRR binomial tree (American put).

    Parameters:
      S: spot price
      strikes: scalar or array of strikes
      T: time to expiration (years)
      r: risk‑free rate
      sigma: volatility
      steps: number of binomial steps
      opt_type: 'c' or 'p'
      american: whether to allow early exercise
      q: continuous dividend yield
    Returns:
      numpy array of prices, one per strike
    """
    strikes_arr = np.atleast_1d(strikes).astype(float)

    # 1) European pricing or American call → Black‑Scholes
    if not american or opt_type == "c":
        return np.array([
            black_scholes_price(S, K, T, r, sigma, option_type=opt_type, q=q)
            for K in strikes_arr
        ])

    # 2) American put via binomial tree
    if S <= 0 or np.any(strikes_arr <= 0):
        raise ValueError("Spot and strikes must be positive")
    if T <= 0:
        raise ValueError("Time to expiration must be positive")
    if sigma < 0:
        raise ValueError("Sigma must be non‑negative")
    if not isinstance(steps, int) or steps < 1:
        raise ValueError("steps must be integer >= 1")
    if opt_type != "p":
        raise ValueError("Binomial tree implementation only supports American puts")

    dt = T / steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    # risk-neutral up-prob with dividend yield q
    p = (np.exp((r - q) * dt) - d) / (u - d)

    # Terminal stock prices: shape (steps+1, 1)
    ups = u ** (np.arange(steps, -1, -1)[:, None])
    downs = d ** (np.arange(0, steps + 1)[:, None])
    ST = S * ups * downs  # (steps+1, 1) broadcastable to (steps+1, n_strikes)

    # Terminal payoff for puts
    payoff = np.maximum(strikes_arr - ST, 0.0)

    # Backward induction with early exercise
    for i in range(steps):
        # discount expected value
        payoff = np.exp(-r * dt) * (p * payoff[1:] + (1 - p) * payoff[:-1])
        # intrinsic value if exercised early
        ups_i = u ** (np.arange(steps - i - 1, -1, -1)[:, None])
        downs_i = d ** (np.arange(0, steps - i)[:, None])
        ST_i = S * ups_i * downs_i
        intrinsic = np.maximum(strikes_arr - ST_i, 0.0)
        payoff = np.maximum(payoff, intrinsic)

    return payoff.flatten()
