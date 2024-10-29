# Original Colab Link: https://colab.research.google.com/drive/1C60BkTkwn6ioU6o3gVwcG22jn3mZ73pB#scrollTo=6ZNC_UxBRo5p
#! C:\Users\potat\Downloads\Automated-Trading\automated-trades-env\Scripts\python.exe

import os
import pymongo
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
from benzinga import financial_data

load_dotenv()

def fetch_data(symbol, date_from, date_to, interval='1D'):
    try:
        fin = financial_data.Benzinga(os.getenv('API_KEY'))
        data = fin.bars(symbol, date_from, date_to, interval)
        candles = data[0]['candles']
        df = pd.DataFrame(candles)
        
        # Store in "Historical Data" Collection
        data = df.to_dict(orient="records")
        uploading_hdata(data)
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()
    
    
    
def prepare_data(symbol, date_from, date_to, interval='1D'):
    try:
        df = fetch_data(symbol, date_from, date_to, interval)
        if df.empty:
            print(f"No data fetched for {symbol}")
            return df
        df = calculate_indicators(df)
        return df
    except Exception as e:
        print(f"Error preparing data for {symbol}: {e}")
        return pd.DataFrame()
    
    

def calculate_indicators(df):
    try:
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
    except Exception as e:
        print(f"Error calculating indicators: {e}")
        return df



def uploading_hdata(training_data):
    try:
        client = pymongo.MongoClient(os.getenv('MONGO_URI'))
        db = client[os.getenv('DATABASE_NAME')]
        collection = db[os.getenv('TRAINING_DATA')]

        try:
            collection.delete_many({})
            collection.insert_many(training_data)
        except Exception as e:
            print(f"Error uploading data to MongoDB: {e}")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
