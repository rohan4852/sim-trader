import threading
import time
from typing import Dict, List
import pandas as pd
from src.orderbook import SimpleOrderBook


class SimulationBackend:
    def __init__(self):
        self.lock = threading.Lock()
        self.thread = None
        self._stop_event = threading.Event()
        self.prices: Dict[str, pd.DataFrame] = {}
        self.engines = {}
        self.portfolio = None
        self.orderbook = SimpleOrderBook()
        self.idx = 0
        self.tick_interval = 0.01
        self.history = []

    def configure(self, prices: Dict[str, pd.DataFrame], engines: Dict[str, object], portfolio, tick_interval=0.01):
        with self.lock:
            self.prices = prices
            self.engines = engines
            self.portfolio = portfolio
            self.tick_interval = float(tick_interval)
            self.idx = 0
            self.history = []
            self._stop_event.clear()

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self._stop_event.clear()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self._stop_event.set()
        if self.thread:
            self.thread.join(timeout=1.0)

    def reset(self):
        with self.lock:
            self.idx = 0
            self.history = []
            if self.portfolio:
                self.portfolio.history = []

    def _run_loop(self):
        # advance until any price series exhausted or stop requested
        while not self._stop_event.is_set():
            with self.lock:
                # determine available symbols and max length
                symbols = list(self.prices.keys())
                if not symbols:
                    break
                # get market prices at current idx
                market_prices = {}
                timestamp = None
                for s in symbols:
                    df = self.prices[s]
                    if self.idx >= len(df):
                        # end simulation when any series ends
                        self._stop_event.set()
                        break
                    row = df.iloc[self.idx]
                    market_prices[s] = float(row['price'])
                    timestamp = row['timestamp'] if timestamp is None else timestamp

                # strategy decisions and trades
                for s, engine in self.engines.items():
                    price = market_prices.get(s)
                    if price is None:
                        continue
                    action = engine.on_price(price)
                    if action == 'BUY':
                        size = int(engine.order_size)
                    elif action == 'SELL':
                        size = -int(engine.order_size)
                    else:
                        size = 0
                    if size != 0:
                        exec_price, executed_size = self.orderbook.execute_market_order(s, size, price)
                        try:
                            self.portfolio.execute_trade(s, executed_size, exec_price)
                        except Exception as e:
                            # ignore or log insufficient position
                            pass
                # mark to market and record snapshot
                snapshot = self.portfolio.mark_to_market(market_prices, timestamp=timestamp)
                snapshot['tick'] = self.idx
                self.history.append(snapshot)
                self.idx += 1
            # sleep outside lock
            time.sleep(self.tick_interval)

    def get_state(self):
        with self.lock:
            return {
                'idx': self.idx,
                'history': list(self.history),
                'portfolio': self.portfolio,
            }


# module-level singleton
_backend = SimulationBackend()


def configure(prices: Dict[str, pd.DataFrame], engines: Dict[str, object], portfolio, tick_interval=0.01):
    _backend.configure(prices, engines, portfolio, tick_interval)


def start():
    _backend.start()


def stop():
    _backend.stop()


def reset():
    _backend.reset()


def get_state():
    return _backend.get_state()


def persist(path="data/portfolio_history.csv"):
    if _backend.portfolio:
        _backend.portfolio.persist_history(path)
