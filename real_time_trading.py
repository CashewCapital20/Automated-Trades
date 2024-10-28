import os
import time
import pandas as pd
from train_model import calculate_indicators
from trade_logs import log_market
from dotenv import load_dotenv
from benzinga import financial_data
from trade_logs import log_trade
import joblib

load_dotenv()
fin = financial_data.Benzinga(os.getenv('API_KEY'))

# Function to fetch real-time data
def fetch_latest_data(symbol, interval='1M'):
    data = fin.bars(symbol, date_from='1d', date_to=None, interval=interval)
    candles = data[0]['candles']
    df = pd.DataFrame(candles)
    return df

# Real-time trading with the trained model
def real_time_trading(symbol, poll_interval=60):
    df = pd.DataFrame()
    model = joblib.load('random_forest_model.joblib')

    while True:
        try:
            latest_data = fetch_latest_data(symbol, interval='1M')

            # Drop duplicates in case of overlapping data
            latest_data.drop_duplicates(subset='time', keep='last', inplace=True)

            # If DataFrame is empty, initialize with the latest data
            if df.empty:
                df = latest_data
            else:
              df = pd.concat([df, latest_data]).drop_duplicates(subset='time', keep='last')

            df = calculate_indicators(df)

            # Ensure indicators have suficient data to work on
            if len(df) >= 26:
                latest_row = df.iloc[-1].copy()

                # Add the computed rows needed to pass into model
                X_real_time = pd.DataFrame({
                    'macd': [latest_row['macd']],
                    'macd_hist': [latest_row['macd_hist']],
                    'rsi': [latest_row['rsi']],
                    'slowk': [latest_row['slowk']],
                    'slowd': [latest_row['slowd']]
                })
                prediction = model.predict(X_real_time)[0]

                # ================ #    
                # Connect with log_market function here or merge 
                # this file with the "log_market" function
                # ================ #    

                # Trade based on prediction
                # if prediction == 1:
                #     print(f"Buy Signal at price: {latest_row['close']} at {latest_row['time']}")
                # elif prediction == -1:
                #     print(f"Sell Signal at price: {latest_row['close']} at {latest_row['time']}")
                # elif prediction == -2:
                #     print(f"Short Signal at price: {latest_row['close']} at {latest_row['time']}")
                # elif prediction == 2:
                #     print(f"Cover Signal at price: {latest_row['close']} at {latest_row['time']}")
                # else:
                #     print(f"Hold at price: {latest_row['close']} at {latest_row['time']}")

        except Exception as e:
            print(f"Error: {e}")

        # Wait 60 seconds
        time.sleep(poll_interval)
        
real_time_trading('NVDA')