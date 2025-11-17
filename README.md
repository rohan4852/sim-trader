# Sim-Trader: Interactive Live Trading Simulation Dashboard

A real-time interactive trading simulator with Streamlit UI that generates synthetic market data, executes trading strategies (moving average crossover), simulates order execution with slippage/commission, tracks multi-symbol portfolios, and visualizes live P&L and market activity.

## Features

✨ **Live Interactive Dashboard**
- Real-time price charts with Streamlit
- Start/Stop/Auto-run simulation controls
- Single-step and background threaded execution modes
- Live P&L and portfolio metrics display

📊 **Advanced Market Simulation**
- Synthetic market data generator with drift, volatility, and jump events
- Configurable orderbook simulator with spread and depth modeling
- Position limits, commission, and slippage support
- Multi-symbol trading support (comma-separated in UI)

🤖 **Trading Strategy**
- Simple moving average (SMA) crossover strategy
- Configurable short/long window parameters
- Automatic buy/sell signal generation

💼 **Portfolio Management**
- Real-time position tracking and PnL calculation
- Realized and unrealized P&L snapshots
- Exposure monitoring with position limits
- CSV persistence for historical analysis

🔌 **Multi-Execution Modes**
- Single-step loop: Click to advance tick-by-tick
- Auto-run: Continuous simulation with configurable delay
- Background threaded runner: Scalable multi-symbol simulation
- Web-based UI: Deploy to Streamlit Cloud

## Tech Stack

- **Python 3.10+**
- **Streamlit** — Interactive web UI
- **Pandas & NumPy** — Data processing and numerical simulation
- **Matplotlib** — Chart rendering
- **Threading** — Background simulation runner
- **Pytest** — Unit testing

## Project Layout

```
sim-trader/
├─ data/
│  └─ portfolio_history.csv       # persisted portfolio snapshots
├─ src/
│  ├─ __init__.py
│  ├─ ui.py                       # Streamlit dashboard (main entry)
│  ├─ generator.py                # synthetic price data generator
│  ├─ engine.py                   # trading strategy (SMA crossover)
│  ├─ portfolio.py                # portfolio + PnL logic with risk params
│  ├─ orderbook.py                # simple orderbook simulator (spread, depth, impact)
│  ├─ sim_backend.py              # threaded simulation runner
│  └─ utils.py                    # helpers (optional)
├─ tests/
│  ├─ test_engine.py
│  ├─ test_generator.py
│  ├─ test_portfolio.py
│  └─ __pycache__/
├─ notebooks/                     # (optional) analysis notebooks
├─ README.md
├─ RESEARCH.md                    # research notes & design decisions
└─ requirements.txt
```

## Installation

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/rohan4852/sim-trader.git
   cd sim-trader
   ```

2. **Create & activate virtual environment**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Streamlit Cloud Deployment

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app" → Select your `sim-trader` repo → Set main file to `src/ui.py`
4. Deploy!

## Quick Start

### Run Streamlit Dashboard (Local)

```bash
streamlit run src/ui.py
```

The app will open at `http://localhost:8501`.

### Usage Workflow

1. **Configure Simulation** (Sidebar)
   - Set symbol(s) (comma-separated, e.g., `SYM,ABC`)
   - Adjust price generation parameters (ticks, drift, volatility, start price)
   - Set strategy windows (short/long MA)
   - Configure risk params (position limit, commission, slippage)
   - Tune orderbook depth and spread

2. **Generate Data**
   - Click **Generate / Reset** → generates price series for all symbols
   - Price chart appears showing the full series

3. **Run Simulation**
   - **Start (single-step loop)** — Advance 1 tick per UI interaction (manual stepping)
   - **Start background runner** — Continuous threaded simulation (fastest)
   - **Auto-run checkbox** — Toggle automatic advance with configurable delay

4. **Monitor Live**
   - Watch price chart update in real-time
   - View recent trades table
   - See cumulative P&L chart
   - Check portfolio metrics (cash, exposure, P&L)

5. **Persist Results**
   - Click **Persist history to CSV** to save run to `data/portfolio_history.csv`

## Configuration Guide

### Strategy Parameters
- **Short MA window** (default: 20): Faster moving average (buy signal when > long)
- **Long MA window** (default: 50): Slower moving average (sell signal when < short)
- **Order size** (default: 10): Number of shares per trade

### Market Parameters
- **Ticks** (default: 1000): Length of price series to generate
- **Start price** (default: 100.0): Initial price
- **Drift (μ)** (default: 0.0): Mean return (trend)
- **Volatility (σ)** (default: 0.01): Standard deviation of returns

### Risk & Execution
- **Position limit** (default: 100000): Max absolute position size
- **Commission** (default: 0.0): Absolute fee per trade
- **Slippage** (default: 0.0): Fraction of price (e.g., 0.001 = 0.1% slippage)
- **Orderbook spread** (default: 0.001): Bid-ask spread fraction
- **Orderbook depth** (default: 1000): Notional available liquidity

## API Examples

### Programmatic Simulation (Backend Runner)

```python
from src.generator import generate_prices
from src.engine import SimpleMAStrategy
from src.portfolio import Portfolio
from src import sim_backend

# Setup
prices = {'SYM': generate_prices(symbol='SYM', n=5000)}
engines = {'SYM': SimpleMAStrategy(short_window=20, long_window=50, order_size=10)}
portfolio = Portfolio(cash=100000, position_limit=100000, commission=0.0, slippage=0.001)

# Configure and run
sim_backend.configure(prices=prices, engines=engines, portfolio=portfolio, tick_interval=0.01)
sim_backend.start()

# Poll state
import time
time.sleep(2)
state = sim_backend.get_state()
print(f"History: {len(state['history'])} snapshots")

# Persist
sim_backend.persist(path="data/portfolio_history.csv")
```

### Manual Stepping

```python
from src.generator import generate_prices
from src.engine import SimpleMAStrategy
from src.portfolio import Portfolio

prices = generate_prices(symbol='SYM', n=100)
engine = SimpleMAStrategy(short_window=20, long_window=50, order_size=10)
portfolio = Portfolio()

for idx, row in prices.iterrows():
    price = row['price']
    signal = engine.on_price(price)
    if signal == 'BUY':
        portfolio.execute_trade('SYM', 10, price)
    elif signal == 'SELL':
        portfolio.execute_trade('SYM', -10, price)
    snapshot = portfolio.mark_to_market({'SYM': price}, timestamp=row['timestamp'])
    print(f"Cash: {snapshot['cash']:.2f}, P&L: {snapshot['realized_pnl']:.2f}")
```

## Testing

Run unit tests:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=src tests/
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Charts empty after Generate/Reset | Normal — click Start to begin simulation |
| No trades executing | Check if signal window is large enough (prices need MA data) |
| Slow performance | Reduce `n_ticks` or use background runner instead of single-step |
| Import errors on Streamlit Cloud | Ensure `sys.path` setup in `ui.py` (already included) |
| Negative prices in chart | Reduce `sigma` or add price floor in generator |

## Architecture Notes

- **State Management**: Streamlit session state stores prices, engines, portfolio, and history
- **Rerun Handling**: Compatibility layer for `st.experimental_rerun()` → `st.query_params`
- **Threading**: Background runner uses thread-safe locks for concurrent access
- **Orderbook**: Simple impact model (execution price adjusts by `size/depth * spread`)

## Future Enhancements

- [ ] Multiple strategies (MACD, RSI, Bollinger Bands)
- [ ] Real market data integration (yfinance, Alpaca)
- [ ] Advanced risk metrics (Sharpe ratio, max drawdown, VaR)
- [ ] Order types (limit, stop-loss)
- [ ] Portfolio backtesting and optimization
- [ ] Real-time data websocket integration
- [ ] Database persistence (SQLite, PostgreSQL)

## Contributing

Contributions welcome! Please open issues or submit PRs.

## License

MIT License — See LICENSE file for details.

## Author

Rohan ([@rohan4852](https://github.com/rohan4852))

---

**Questions?** Open an issue on GitHub or check [RESEARCH.md](RESEARCH.md) for design details.