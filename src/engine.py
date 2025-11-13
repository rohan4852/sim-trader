# src/engine.py
import pandas as pd

class SimpleMAStrategy:
    def __init__(self, short_window=20, long_window=50, order_size=10):
        self.short_window = short_window
        self.long_window = long_window
        self.order_size = order_size
        self.prices = []

    def on_price(self, price):
        self.prices.append(price)
        if len(self.prices) < self.long_window:
            return None
        s = pd.Series(self.prices)
        short_ma = s.rolling(self.short_window).mean().iloc[-1]
        long_ma = s.rolling(self.long_window).mean().iloc[-1]
        if short_ma > long_ma:
            return "BUY"
        elif short_ma < long_ma:
            return "SELL"
        return None
