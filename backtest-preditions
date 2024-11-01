import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Calculate Returns
df['returns'] = df['close'].pct_change()

# Cumulative Returns
df['cumulative_returns'] = (1 + df['returns']).cumprod()

# Calculate Sharpe Ratio
def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    return (returns.mean() - risk_free_rate) / returns.std() * np.sqrt(252)

# Calculate Max Drawdown
def calculate_max_drawdown(cumulative_returns):
    drawdown = cumulative_returns / cumulative_returns.cummax() - 1
    return drawdown.min()

# Calculate Profit Factor
def calculate_profit_factor(profit_trades, loss_trades):
    return abs(profit_trades.sum() / loss_trades.sum())

# Calculate Win Rate
def calculate_win_rate(profitable_trades, total_trades):
    return len(profitable_trades) / total_trades

# Assuming trades_df contains individual trade data with columns: 'profit_loss'
profitable_trades = trades_df[trades_df['profit_loss'] > 0]
loss_trades = trades_df[trades_df['profit_loss'] < 0]
total_trades = len(trades_df)

# Metric Calculation
sharpe_ratio = calculate_sharpe_ratio(df['returns'])
max_drawdown = calculate_max_drawdown(df['cumulative_returns'])
profit_factor = calculate_profit_factor(profitable_trades['profit_loss'], loss_trades['profit_loss'])
win_rate = calculate_win_rate(profitable_trades, total_trades)

# Display metrics
print(f"Sharpe Ratio: {sharpe_ratio}")
print(f"Maximum Drawdown: {max_drawdown}")
print(f"Profit Factor: {profit_factor}")
print(f"Win Rate: {win_rate}")

# Plotting Cumulative Returns and Drawdowns
plt.figure(figsize=(14, 7))

# Cumulative Returns Plot
plt.subplot(2, 1, 1)
plt.plot(df['cumulative_returns'], label='Cumulative Returns')
plt.title("Cumulative Returns")
plt.legend()

# Drawdown Plot
plt.subplot(2, 1, 2)
df['drawdown'] = df['cumulative_returns'] / df['cumulative_returns'].cummax() - 1
plt.plot(df['drawdown'], color='red', label='Drawdown')
plt.title("Drawdown")
plt.legend()
plt.tight_layout()
plt.show()
