# src/portfolio.py
import pandas as pd

class Portfolio:
    def __init__(self, cash=100000.0):
        self.cash = cash
        self.positions = {}  # symbol -> {'size': int, 'avg_price': float}
        self.realized_pnl = 0.0
        self.history = []  # record trades and PnL snapshots

    def execute_trade(self, symbol, size, price):
        # size positive => buy, negative => sell
        cost = size * price
        if size > 0:  # buy
            self._buy(symbol, size, price, cost)
        else:  # sell
            self._sell(symbol, -size, price, -cost)  # convert to positive size

    def _buy(self, symbol, size, price, cost):
        pos = self.positions.get(symbol)
        if pos:
            new_size = pos['size'] + size
            avg_price = (pos['avg_price'] * pos['size'] + price * size) / new_size
            pos['size'] = new_size
            pos['avg_price'] = avg_price
        else:
            self.positions[symbol] = {'size': size, 'avg_price': price}
        self.cash -= cost

    def _sell(self, symbol, size, price, proceeds):
        pos = self.positions.get(symbol)
        if not pos or pos['size'] < size:
            raise ValueError("Not enough position to sell")
        pnl = (price - pos['avg_price']) * size
        pos['size'] -= size
        if pos['size'] == 0:
            del self.positions[symbol]
        self.realized_pnl += pnl
        self.cash += proceeds  # proceeds is positive for sell

    def mark_to_market(self, market_prices: dict, timestamp=None):
        unreal = 0.0
        exposure = {}
        for sym, pos in self.positions.items():
            mprice = market_prices.get(sym)
            if mprice is None: continue
            unreal += (mprice - pos['avg_price']) * pos['size']
            exposure[sym] = pos['size'] * mprice
        total_exposure = sum(exposure.values())
        snapshot = {"timestamp": timestamp, "cash": self.cash, "realized_pnl": self.realized_pnl,
                    "unrealized_pnl": unreal, "total_exposure": total_exposure}
        self.history.append(snapshot)
        return snapshot
