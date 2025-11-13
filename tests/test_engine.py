import pytest
from src.engine import SimpleMAStrategy

def test_strategy_initialization():
    strat = SimpleMAStrategy(short_window=5, long_window=10, order_size=20)
    assert strat.short_window == 5
    assert strat.long_window == 10
    assert strat.order_size == 20
    assert strat.prices == []

def test_strategy_no_signal_early():
    strat = SimpleMAStrategy(short_window=5, long_window=10)
    for i in range(9):
        signal = strat.on_price(100)
        assert signal is None

def test_strategy_buy_signal():
    strat = SimpleMAStrategy(short_window=2, long_window=3)
    # Prices: 100, 101, 102 -> short MA: (101+102)/2=101.5, long MA: (100+101+102)/3=101 -> 101.5 > 101 -> BUY
    strat.on_price(100)
    strat.on_price(101)
    signal = strat.on_price(102)
    assert signal == "BUY"

def test_strategy_sell_signal():
    strat = SimpleMAStrategy(short_window=2, long_window=3)
    # Prices: 102, 101, 100 -> short MA: (101+100)/2=100.5, long MA: (102+101+100)/3=101 -> 100.5 < 101 -> SELL
    strat.on_price(102)
    strat.on_price(101)
    signal = strat.on_price(100)
    assert signal == "SELL"
