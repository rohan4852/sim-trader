# src/runner.py
from .generator import generate_prices
from .engine import SimpleMAStrategy
from .portfolio import Portfolio

df = generate_prices(n=1000)
strat = SimpleMAStrategy(short_window=5, long_window=20, order_size=10)
port = Portfolio(cash=100000)

for _, row in df.iterrows():
    signal = strat.on_price(row['price'])
    if signal == "BUY":
        port.execute_trade(row['symbol'], size=strat.order_size, price=row['price'])
    elif signal == "SELL":
        # naive: close full position if exists
        pos = port.positions.get(row['symbol'])
        if pos:
            port.execute_trade(row['symbol'], size=-pos['size'], price=row['price'])
    port.mark_to_market({row['symbol']: row['price']}, timestamp=row['timestamp'])

# Save history to CSV
import pandas as pd
hist_df = pd.DataFrame(port.history)
hist_df.to_csv("data/portfolio_history.csv", index=False)

# Print final numbers
final = port.history[-1]
print(f"Final Cash: {final['cash']}")
print(f"Realized P&L: {final['realized_pnl']}")
print(f"Unrealized P&L: {final['unrealized_pnl']}")
print(f"Total Exposure: {final['total_exposure']}")
