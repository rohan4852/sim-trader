# src/portfolio.py
import pandas as pd

class Portfolio:
    def __init__(self, cash=100000.0, position_limit=100000, commission=0.0, slippage=0.0):
        self.cash = float(cash)
        self.positions = {}  # symbol -> {'size': int, 'avg_price': float}
        self.realized_pnl = 0.0
        self.history = []  # record trades and PnL snapshots
        self.position_limit = int(position_limit)
        self.commission = float(commission)  # absolute per-trade cost
        self.slippage = float(slippage)  # fraction of price (e.g., 0.001)

    def execute_trade(self, symbol, size, price):
        """
        Execute a market order for `size` shares (positive buy, negative sell).
        Applies slippage and commission and enforces position limits.
        Returns dict with execution details.
        """
        if size == 0:
            return None

        # apply slippage: worst fill for the initiator
        if size > 0:
            exec_price = price * (1 + abs(self.slippage))
        else:
            exec_price = price * (1 - abs(self.slippage))

        # enforce position limit
        current = self.positions.get(symbol, {'size': 0})['size']
        proposed = current + size
        if abs(proposed) > self.position_limit:
            raise ValueError(f"Position limit exceeded for {symbol}")

        notional = exec_price * size
        # commission is charged per-trade (absolute)
        self.cash -= (notional + self.commission)

        if size > 0:
            self._buy(symbol, size, exec_price)
            side = 'BUY'
        else:
            self._sell(symbol, -size, exec_price)
            side = 'SELL'

        return {'symbol': symbol, 'size': size, 'price': exec_price, 'commission': self.commission, 'side': side}

    def _buy(self, symbol, size, price):
        pos = self.positions.get(symbol)
        if pos:
            new_size = pos['size'] + size
            avg_price = (pos['avg_price'] * pos['size'] + price * size) / new_size
            pos['size'] = new_size
            pos['avg_price'] = avg_price
        else:
            self.positions[symbol] = {'size': size, 'avg_price': price}

    def _sell(self, symbol, size, price):
        pos = self.positions.get(symbol)
        if not pos or pos['size'] < size:
            raise ValueError("Not enough position to sell")
        pnl = (price - pos['avg_price']) * size
        pos['size'] -= size
        if pos['size'] == 0:
            del self.positions[symbol]
        self.realized_pnl += pnl

    def mark_to_market(self, market_prices: dict, timestamp=None):
        """Create a snapshot with cash, realized/unrealized pnl, exposures, and timestamp."""
        unreal = 0.0
        exposure = {}
        for sym, pos in list(self.positions.items()):
            mprice = market_prices.get(sym)
            if mprice is None:
                continue
            unreal += (mprice - pos['avg_price']) * pos['size']
            exposure[sym] = pos['size'] * mprice
        total_exposure = sum(exposure.values())
        snapshot = {
            "timestamp": timestamp,
            "cash": float(self.cash),
            "realized_pnl": float(self.realized_pnl),
            "unrealized_pnl": float(unreal),
            "total_exposure": float(total_exposure),
            "positions": {s: dict(v) for s, v in self.positions.items()},
        }
        self.history.append(snapshot)
        return snapshot

    def persist_history(self, path="data/portfolio_history.csv"):
        """Write current history to CSV (appends if file exists)."""
        import os
        import pandas as pd
        if not self.history:
            return
        df = pd.DataFrame(self.history)
        # flatten positions to JSON string
        df['positions'] = df['positions'].apply(lambda x: str(x))
        header = not os.path.exists(path)
        df.to_csv(path, mode='a', index=False, header=header)