import threading

class SimpleOrderBook:
    """A minimal orderbook simulator. It doesn't match limit orders — it simulates
    market impact and available liquidity. For market orders it returns an execution
    price adjusted by impact = size / depth * spread.
    """
    def __init__(self, depth=1000, spread=0.001):
        self.depth = float(depth)
        self.spread = float(spread)  # relative
        self.lock = threading.Lock()

    def execute_market_order(self, symbol, size, mid_price):
        """Return (executed_price, executed_size).
        executed_price adjusted by impact proportional to |size|/depth.
        """
        with self.lock:
            impact = (abs(size) / (self.depth + 1e-9)) * self.spread
            if size > 0:
                exec_price = mid_price * (1 + impact)
            else:
                exec_price = mid_price * (1 - impact)
            return exec_price, size
