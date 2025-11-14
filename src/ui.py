import time
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from . import generator
from src.engine import SimpleMAStrategy
from src.portfolio import Portfolio
from src import sim_backend
from src.orderbook import SimpleOrderBook

st.set_page_config(page_title="Sim-Trader Dashboard", layout="wide")
st.title("Sim-Trader Dashboard — Live Simulation")


def init_state():
	if 'running' not in st.session_state:
		st.session_state.running = False
	if 'auto' not in st.session_state:
		st.session_state.auto = False
	if 'idx' not in st.session_state:
		st.session_state.idx = 0
	if 'prices' not in st.session_state:
		st.session_state.prices = None
	if 'engine' not in st.session_state:
		st.session_state.engine = None
	if 'portfolio' not in st.session_state:
		st.session_state.portfolio = None
	if 'history_df' not in st.session_state:
		st.session_state.history_df = pd.DataFrame()
	if 'engines' not in st.session_state:
		st.session_state.engines = {}


init_state()


# Helper for forcing a rerun in a Streamlit-version-compatible way
def request_rerun():
	# prefer official API if present
	if hasattr(st, 'experimental_rerun'):
		try:
			st.experimental_rerun()
			return
		except Exception:
			pass
	# fallback: change a query param which triggers a rerun
	try:
		st.experimental_set_query_params(_sim_rerun=int(time.time() * 1000))
	except Exception:
		# last resort: no-op
		return


with st.sidebar:
	st.header("Simulation Controls")
	# multi-symbol support (comma separated)
	symbols_txt = st.text_input("Symbols (comma separated)", value="SYM")
	symbol = symbols_txt.split(",")[-1].strip() if symbols_txt else "SYM"
	symbols = [s.strip() for s in symbols_txt.split(",") if s.strip()]
	n_ticks = st.number_input("Ticks (n)", min_value=100, max_value=100000, value=1000, step=100)
	start_price = st.number_input("Start price", value=100.0)
	mu = st.number_input("Drift (mu)", value=0.0, format="%f")
	sigma = st.number_input("Volatility (sigma)", value=0.01, format="%f")
	short_w = st.number_input("Short MA window", min_value=1, max_value=500, value=20)
	long_w = st.number_input("Long MA window", min_value=2, max_value=2000, value=50)
	order_size = st.number_input("Order size", min_value=1, max_value=100000, value=10)
	delay = st.number_input("Delay (s)", min_value=0.0, max_value=5.0, value=0.2, format="%f")

	# risk/execution params
	position_limit = st.number_input("Position limit", min_value=1, max_value=10000000, value=100000)
	commission = st.number_input("Commission (abs)", min_value=0.0, max_value=1000.0, value=0.0, format="%f")
	slippage = st.number_input("Slippage (fraction)", min_value=0.0, max_value=0.1, value=0.0, format="%f")
	# orderbook params
	ob_depth = st.number_input("Orderbook depth", min_value=1, max_value=1000000, value=1000)
	ob_spread = st.number_input("Orderbook spread (fraction)", min_value=0.0, max_value=0.1, value=0.001, format="%f")
	tick_interval = st.number_input("Tick interval (s)", min_value=0.0, max_value=1.0, value=0.01, format="%f")
	st.write("")
	if st.button("Generate / Reset"):
		# generate price series for all symbols
		prices = {}
		for s in symbols:
			prices[s] = generator.generate_prices(symbol=s, n=n_ticks, start_price=start_price, mu=mu, sigma=sigma)
		st.session_state.prices = prices
		st.session_state.idx = 0
		# create engines and portfolio with params
		engines = {s: SimpleMAStrategy(short_window=int(short_w), long_window=int(long_w), order_size=int(order_size)) for s in symbols}
		portfolio = Portfolio(position_limit=int(position_limit), commission=float(commission), slippage=float(slippage))
		st.session_state.engines = engines
		st.session_state.portfolio = portfolio
		st.session_state.history_df = pd.DataFrame()
		st.session_state.running = False

	start_local = st.button("Start (single-step loop)")
	stop_local = st.button("Stop (single-step loop)")
	start_bg = st.button("Start background runner")
	stop_bg = st.button("Stop background runner")
	persist_btn = st.button("Persist history to CSV")
	if start_local:
		# fallback to previous per-tick stepping behavior (single-symbol)
		if not symbols:
			st.warning("Please specify at least one symbol")
		else:
			# initialize if needed
			if 'prices' not in st.session_state or not st.session_state.prices:
				st.session_state.prices = {s: generator.generate_prices(symbol=s, n=n_ticks, start_price=start_price, mu=mu, sigma=sigma) for s in symbols}
			st.session_state.engine = SimpleMAStrategy(short_window=int(short_w), long_window=int(long_w), order_size=int(order_size))
			st.session_state.portfolio = Portfolio(position_limit=int(position_limit), commission=float(commission), slippage=float(slippage))
			st.session_state.history_df = pd.DataFrame()
			st.session_state.idx = 0
			st.session_state.running = True
			st.session_state.auto = True

	if stop_local:
		st.session_state.running = False
		st.session_state.auto = False

	if start_bg:
		if not symbols:
			st.warning("Please specify symbols to run background simulation")
		else:
			# prepare engines and prices
			prices = {s: generator.generate_prices(symbol=s, n=n_ticks, start_price=start_price, mu=mu, sigma=sigma) for s in symbols}
			engines = {s: SimpleMAStrategy(short_window=int(short_w), long_window=int(long_w), order_size=int(order_size)) for s in symbols}
			portfolio = Portfolio(position_limit=int(position_limit), commission=float(commission), slippage=float(slippage))
			# configure simple orderbook
			ob = SimpleOrderBook(depth=int(ob_depth), spread=float(ob_spread))
			# attach custom orderbook to backend
			sim_backend._backend.orderbook = ob
			sim_backend.configure(prices=prices, engines=engines, portfolio=portfolio, tick_interval=float(tick_interval))
			sim_backend.start()
			st.session_state.running_bg = True

	if stop_bg:
		sim_backend.stop()
		st.session_state.running_bg = False

	if persist_btn:
		# persist any portfolio history available
		try:
			sim_backend.persist(path="data/portfolio_history.csv")
			st.success("Persisted history to data/portfolio_history.csv")
		except Exception as e:
			st.error(f"Persist failed: {e}")

	st.session_state.auto = st.checkbox("Auto-run", value=st.session_state.auto)


cols = st.columns([2, 1])

with cols[0]:
	st.subheader("Price / Orders")
	price_plot_placeholder = st.empty()
	trades_placeholder = st.empty()

with cols[1]:
	st.subheader("Portfolio Metrics")
	metrics_placeholder = st.empty()


def step_simulation():
	# run a single tick
	idx = st.session_state.idx
	prices = st.session_state.prices
	# support dict of symbol->DataFrame or a single DataFrame
	if isinstance(prices, dict):
		prices_df = prices.get(symbol)
	else:
		prices_df = prices
	# engine can be per-symbol (st.session_state.engines) or single engine
	engine = None
	if isinstance(st.session_state.get('engines', None), dict) and st.session_state.get('engines'):
		engine = st.session_state.get('engines').get(symbol)
	else:
		engine = st.session_state.get('engine')
	portfolio = st.session_state.portfolio
	if prices_df is None or idx >= len(prices_df):
		st.session_state.running = False
		return

	row = prices_df.iloc[idx]
	price = float(row['price'])
	timestamp = row['timestamp']

	# strategy decision (single-symbol engine for local stepping)
	decision = engine.on_price(price) if engine is not None else None
	trade_info = None
	if decision == 'BUY':
		try:
			portfolio.execute_trade(symbol, int(order_size), price)
			trade_info = f"BUY {int(order_size)} @ {price:.2f}"
		except Exception as e:
			trade_info = f"BUY failed: {e}"
	elif decision == 'SELL':
		try:
			portfolio.execute_trade(symbol, -int(order_size), price)
			trade_info = f"SELL {int(order_size)} @ {price:.2f}"
		except Exception as e:
			trade_info = f"SELL failed: {e}"

	# mark to market and record
	snapshot = portfolio.mark_to_market({symbol: price}, timestamp=timestamp)
	if trade_info:
		snapshot['last_trade'] = trade_info
	else:
		snapshot['last_trade'] = None

	# append to history df
	hdf = st.session_state.history_df
	new_row = pd.DataFrame([snapshot])
	st.session_state.history_df = pd.concat([hdf, new_row], ignore_index=True)

	st.session_state.idx += 1
	return snapshot


def render_ui():
	# render price chart
	prices = st.session_state.prices
	hdf = st.session_state.history_df
	idx = st.session_state.idx

	# if prices is a dict, show the selected symbol series
	if prices is not None:
		if isinstance(prices, dict):
			prices_df = prices.get(symbol)
		else:
			prices_df = prices
		if prices_df is not None and len(prices_df) > 0:
			recent = prices_df.iloc[:max(1, idx)]
			fig, ax = plt.subplots()
			ax.plot(recent['timestamp'], recent['price'], label='price')
			ax.set_title(f"{symbol} price (ticks: {idx}/{len(prices_df)})")
			ax.set_xlabel('Time')
			ax.set_ylabel('Price')
			ax.legend()
			price_plot_placeholder.pyplot(fig)

	# trades / history
	if not hdf.empty:
		trades_placeholder.dataframe(hdf.tail(10))
		fig2, ax2 = plt.subplots()
		hdf.set_index(pd.to_datetime(hdf['timestamp']), inplace=False)[['realized_pnl','unrealized_pnl']].cumsum().plot(ax=ax2)
		ax2.set_title('Cumulative P&L')
		ax2.set_ylabel('P&L')
		metrics_placeholder.write(hdf.iloc[-1].to_dict())
		st.pyplot(fig2)
	else:
		trades_placeholder.write("No trades yet")
		metrics_placeholder.write({})


# Main loop: advance one step when running
if st.session_state.get('running_bg'):
	# when background runner is active, poll its state and render
	state = sim_backend.get_state()
	h = state.get('history', [])
	if h:
		st.session_state.history_df = pd.DataFrame(h)
	render_ui()
	# auto-refresh while running
	time.sleep(0.1)
	request_rerun()
elif st.session_state.running:
	# local single-step mode
	step_simulation()
	render_ui()
	if st.session_state.auto:
		time.sleep(delay)
		request_rerun()
else:
	render_ui()


# Helper for forcing a rerun in a Streamlit-version-compatible way
def request_rerun():
	# prefer official API if present
	if hasattr(st, 'experimental_rerun'):
		try:
			st.experimental_rerun()
			return
		except Exception:
			pass
	# fallback: change a query param which triggers a rerun
	try:
		st.experimental_set_query_params(_sim_rerun=int(time.time() * 1000))
	except Exception:
		# last resort: no-op
		return

