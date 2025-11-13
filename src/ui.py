import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Sim-Trader Dashboard")

# Load portfolio history
hist = pd.read_csv("data/portfolio_history.csv", parse_dates=['timestamp'])

st.subheader("Portfolio History")
st.dataframe(hist)

st.subheader("Cumulative P&L")
fig, ax = plt.subplots()
(hist.set_index('timestamp')[['realized_pnl','unrealized_pnl']].cumsum()).plot(ax=ax)
ax.set_title('Cumulative P&L')
ax.set_ylabel('P&L')
ax.set_xlabel('Time')
st.pyplot(fig)

st.subheader("Final Metrics")
final = hist.iloc[-1]
st.write(f"Cash: {final['cash']}")
st.write(f"Realized P&L: {final['realized_pnl']}")
st.write(f"Unrealized P&L: {final['unrealized_pnl']}")
st.write(f"Total Exposure: {final['total_exposure']}")
