import pytest
from src.portfolio import Portfolio

def test_buy_sell():
    p = Portfolio(cash=1000)
    p.execute_trade('A', size=10, price=10)   # buy 10 @ 10
    p.execute_trade('A', size=-10, price=12)  # sell 10 @ 12
    assert round(p.realized_pnl, 2) == 20
    assert p.cash == 1000 + 20  # cash back + pnl

def test_portfolio_initialization():
    p = Portfolio(cash=50000)
    assert p.cash == 50000
    assert p.realized_pnl == 0.0
    assert p.positions == {}

def test_buy_multiple():
    p = Portfolio(cash=1000)
    p.execute_trade('A', size=5, price=10)
    p.execute_trade('A', size=5, price=12)
    assert p.positions['A']['size'] == 10
    assert p.positions['A']['avg_price'] == 11.0
    assert p.cash == 1000 - 5*10 - 5*12

def test_sell_insufficient():
    p = Portfolio(cash=1000)
    p.execute_trade('A', size=5, price=10)
    with pytest.raises(ValueError):
        p.execute_trade('A', size=-10, price=12)

def test_mark_to_market():
    p = Portfolio(cash=1000)
    p.execute_trade('A', size=10, price=10)
    snapshot = p.mark_to_market({'A': 12})
    assert snapshot['unrealized_pnl'] == 20
    assert snapshot['total_exposure'] == 120
