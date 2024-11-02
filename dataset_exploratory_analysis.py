import os
from benzinga import financial_data
import numpy as np
import pandas as pd
from fetch_load_mongo import calculate_indicators
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

def fetch_data(stocks, interval='1D'):
    dfs = []
    
    # 365 days for training data + up to 26 days for EMA
    start_date = (datetime.now() - timedelta(days=383)).strftime('%Y-%m-%d')
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        for s in stocks: 
            fin = financial_data.Benzinga(os.getenv('API_KEY'))
            data = fin.bars(s, start_date, end_date, interval)
            df = pd.DataFrame(data[0]['candles'])
            dfs.append(df)
    except Exception as e:
        print(f"Error with fetching data from Benzinga API: {e}")

    return dfs
        

def plot_indicators(df, symbol):
    # Create figure and set size
    fig, axes = plt.subplots(nrows=4, ncols=1, figsize=(14, 10), sharex=True)

    # Plot Close Price
    sns.lineplot(x=df.index, y=df['close'], ax=axes[0], color='blue', label='Close Price')
    axes[0].set_title(f'{symbol} Close Price')
    axes[0].legend()

    # Plot MACD with Signal Line and Histogram
    sns.lineplot(x=df.index, y=df['macd'], ax=axes[1], color='green', label='MACD')
    sns.lineplot(x=df.index, y=df['macd_signal'], ax=axes[1], color='red', label='MACD Signal')
    axes[1].bar(df.index, df['macd_hist'], color='gray', alpha=0.3, label='MACD Histogram')
    axes[1].set_title(f'{symbol} MACD')
    axes[1].legend()

    # Plot Stochastic Oscillator (%K and %D)
    sns.lineplot(x=df.index, y=df['slowk'], ax=axes[2], color='purple', label='Stochastic %K')
    sns.lineplot(x=df.index, y=df['slowd'], ax=axes[2], color='orange', label='Stochastic %D')
    axes[2].axhline(80, linestyle='--', color='red', alpha=0.5)  # Overbought line
    axes[2].axhline(20, linestyle='--', color='green', alpha=0.5)  # Oversold line
    axes[2].set_title(f'{symbol} Stochastic Oscillator')
    axes[2].legend()

    # Plot RSI
    sns.lineplot(x=df.index, y=df['rsi'], ax=axes[3], color='brown', label='RSI')
    axes[3].axhline(70, linestyle='--', color='red', alpha=0.5)  # Overbought line
    axes[3].axhline(30, linestyle='--', color='green', alpha=0.5)  # Oversold line
    axes[3].set_title(f'{symbol} RSI')
    axes[3].legend()

    # Final formatting
    plt.tight_layout()
    plt.show()


# ======================================= #
 
stocks = ["GOOG", "SPY", "AMZN", "NVDA"]    # sample set of companies
dfs = fetch_data(stocks)
# print(dfs)

for symbol, df in zip(stocks, dfs):
    df = calculate_indicators(df)
    df = df.iloc[15:]
    
    print("\nTicker Symbol:", symbol)
    print(df.isna().sum())
    plot_indicators(symbol, df)
    