#! C:\Users\potat\Downloads\Automated-Trading\automated-trades-env\Scripts\python.exe

import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from benzinga import financial_data

# Constants
BALANCE = 10000
QUANTITY = 50

def paper_trade_test():
    # Define the date range
    to_date = datetime.now().strftime('%Y-%m-%d')
    from_date = '2024-01-01'
    
    # Generate a random date within the specified range
    date_range = pd.date_range(start=from_date, end=to_date)
    rand_date = np.random.choice(date_range)

    # Create a date range for 1-minute intervals on rand_date
    rand_date_start = pd.to_datetime(rand_date)
    rand_date_start_str = rand_date_start.strftime('%Y-%m-%d')

    rand_date_end = rand_date_start + timedelta(days=26)
    rand_date_end_str = rand_date_end.strftime('%Y-%m-%d')

    # Fetch financial data for the random date
    fin = financial_data.Benzinga(os.getenv('API_KEY'))
    data = fin.bars('FTV', rand_date_start_str, rand_date_end_str, '1D')
    candles = data[0]['candles']
    df = pd.DataFrame(candles)
    
    one_minute_candles = fin.bars('FTV', rand_date_start_str, rand_date_end_str, '1D')
        
    model = joblib.load('random_forest_model.joblib')
    real_time_trading('FTV', model, one_minute_intervals)

def calculate_indicators(df):
    # Calculate EMA, RSI, and Stochastic Oscillator
    df['ema_fast'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=26, adjust=False).mean()
    
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['rsi'] = 100 - (100 / (1 + (gain / loss)))

    lowest_low = df['low'].rolling(window=14).min()
    highest_high = df['high'].rolling(window=14).max()
    df['slowk'] = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))
    df['slowd'] = df['slowk'].rolling(window=3).mean()
    
    df['macd'] = df['ema_fast'] - df['ema_slow']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']
    
    return df

def real_time_trading(symbol, model, one_minute_intervals):
    df = pd.DataFrame()
    last_action = None  # Track the last action taken

    for timestamp in one_minute_intervals:
        try:
            # Get data for the current timestamp
            current_data = df[df['time'] == timestamp]  # Filter for the current timestamp

            if not current_data.empty:
                # Calculate indicators only if we have sufficient data
                df = calculate_indicators(current_data)

                # Ensure sufficient data for prediction
                if len(df) >= 26:
                    latest_row = df.iloc[-1].copy()
                    
                    X_real_time = pd.DataFrame({
                        'macd': [latest_row['macd']],
                        'macd_hist': [latest_row['macd_hist']],
                        'rsi': [latest_row['rsi']],
                        'slowk': [latest_row['slowk']],
                        'slowd': [latest_row['slowd']]
                    })

                    prediction = model.predict(X_real_time)[0]
                    execute_trade(prediction, latest_row)

            # Sleep briefly to simulate real-time processing
            time.sleep(1)  # Adjust as necessary for testing

        except Exception as e:
            print(f"Error: {e}")

def execute_trade(prediction, latest_row):
    action_map = {
        1: lambda: buy(latest_row['close']),
        -1: lambda: sell(latest_row['close']),
        -2: lambda: short(latest_row['close']),
        2: lambda: cover(latest_row['close']),
    }

    # Execute the corresponding action based on prediction
    action = action_map.get(prediction, lambda: hold(latest_row['close']))
    action()  # Call the action

def buy(price):
    global START_BALANCE
    if START_BALANCE >= price * BUY_QUANTITY:
        START_BALANCE -= price * BUY_QUANTITY
        print(f"Bought {BUY_QUANTITY} shares at {price}. New balance: {START_BALANCE}")
    else:
        print("Insufficient balance to buy.")

def sell(price):
    global START_BALANCE
    START_BALANCE += price * BUY_QUANTITY
    print(f"Sold {BUY_QUANTITY} shares at {price}. New balance: {START_BALANCE}")

def short(price):
    print(f"Shorted {BUY_QUANTITY} shares at {price}.")

def cover(price):
    print(f"Covered short for {BUY_QUANTITY} shares at {price}.")

def hold(price):
    print(f"Holding at price: {price}. Current balance: {START_BALANCE}")
    
paper_trade_test()
print(f"Ending balance: {BALANCE} \n Inventory: {QUANTITY}")