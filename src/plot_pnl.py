import pandas as pd
import matplotlib.pyplot as plt

# Load the portfolio history
hist = pd.read_csv("data/portfolio_history.csv", parse_dates=['timestamp']).set_index('timestamp')

# Plot cumulative P&L
hist[['realized_pnl','unrealized_pnl']].cumsum().plot()
plt.title('Cumulative P&L')
plt.ylabel('P&L')
plt.xlabel('Time')
plt.legend(['Realized P&L', 'Unrealized P&L'])
plt.show()
