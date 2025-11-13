# Sim-Trader: Simulated Trading Platform

A self-contained Python simulated trading platform that generates synthetic market data, executes a trading strategy (moving average crossover), and tracks P&L and exposure.

## Features

- Synthetic market data generator with random walk, drift, volatility, and occasional jumps
- Simple moving average crossover trading strategy
- Portfolio management with position tracking, realized/unrealized P&L, and exposure
- Batch processing with CSV output
- Basic visualization with matplotlib
- Unit tests for core components

## Tech Stack

- Python 3.10+
- Libraries: numpy, pandas, matplotlib, streamlit, pytest

## Project Layout

```
sim-trader/
├─ data/                   # raw generated CSVs
├─ src/
│  ├─ generator.py         # synthetic market data generator
│  ├─ engine.py            # trading engine (strategy + execution)
│  ├─ portfolio.py         # position, PnL, exposure logic
│  ├─ runner.py            # orchestrates generator -> engine -> portfolio (batch/stream)
│  └─ utils.py             # helpers/logging
├─ notebooks/              # optional: analysis / plots
├─ tests/                  # unit tests
├─ README.md
└─ requirements.txt
```

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Unix)
4. Install dependencies: `pip install -r requirements.txt`

## Usage

### Running the Simulation

Run the main simulation script:

```bash
python -m src.runner
```

This will generate synthetic price data, run the trading strategy, and output portfolio history to `data/portfolio_history.csv`. It will also print final cash, realized P&L, unrealized P&L, and total exposure.

### Strategy Parameters

- Short MA window: 5 periods
- Long MA window: 20 periods
- Order size: 10 units

### Visualization

After running the simulation, you can visualize the results using the included plotting script:

```python
import pandas as pd
import matplotlib.pyplot as plt

hist = pd.read_csv("data/portfolio_history.csv", parse_dates=['timestamp']).set_index('timestamp')
hist[['realized_pnl','unrealized_pnl']].cumsum().plot()
plt.title('Cumulative P&L')
plt.show()
```

### Streamlit UI (Optional)

For an interactive UI, create `src/ui.py`:

```python
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Sim-Trader Dashboard")

hist = pd.read_csv("data/portfolio_history.csv", parse_dates=['timestamp'])

st.subheader("Portfolio History")
st.dataframe(hist)

st.subheader("Cumulative P&L")
fig, ax = plt.subplots()
(hist.set_index('timestamp')[['realized_pnl','unrealized_pnl']].cumsum()).plot(ax=ax)
st.pyplot(fig)

st.subheader("Final Metrics")
final = hist.iloc[-1]
st.write(f"Cash: {final['cash']}")
st.write(f"Realized P&L: {final['realized_pnl']}")
st.write(f"Unrealized P&L: {final['unrealized_pnl']}")
st.write(f"Total Exposure: {final['total_exposure']}")
```

Run with: `streamlit run src/ui.py`

## Testing

Run unit tests:

```bash
pytest
```

## Debugging

- If positions sell incorrectly: Check position state after each trade
- If P&L is off: Verify sign conventions (buys reduce cash; sells increase cash; realized P&L computation)
- If generator produces negative prices: Reduce sigma or add minimum price clamp
- If slow: Reduce n or vectorize generator using numpy arrays
