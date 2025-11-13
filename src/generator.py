import numpy as np
import pandas as pd

def generate_prices(symbol="SYM", n=1000, start_price=100.0, mu=0.0, sigma=0.01, seed=42, jump_prob=0.001, jump_scale=0.05):
    np.random.seed(seed)
    prices = [start_price]
    for i in range(1, n):
        # small Gaussian move
        ret = np.random.normal(loc=mu, scale=sigma)
        # occasional jump
        if np.random.rand() < jump_prob:
            ret += np.random.normal(loc=0, scale=jump_scale)
        prices.append(prices[-1] * (1 + ret))
    times = pd.date_range("2025-01-01", periods=n, freq="T")  # 1-minute ticks
    df = pd.DataFrame({"timestamp": times, "symbol": symbol, "price": prices})
    return df