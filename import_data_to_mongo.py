# Original Colab Link: https://colab.research.google.com/drive/1C60BkTkwn6ioU6o3gVwcG22jn3mZ73pB#scrollTo=6ZNC_UxBRo5p

import os
import json
import pymongo
import pandas as pd
import numpy as np
from dotenv import load_dotenv 
# from pymongo import MongoClient
from benzinga import financial_data
from train_model import calculate_indicators

load_dotenv()

# Fetch historical data and store them in DataFrame
def fetch_data(symbol, date_from, date_to, interval):
    fin = financial_data.Benzinga(os.getenv('API_KEY'))
    data = fin.bars(symbol, date_from, date_to, interval)
    candles = data[0]['candles']
    df = pd.DataFrame(candles)

    # Store in "Historical Data" Collection
    data = df.to_dict(orient = "records")
    uploading_hdata(data)

    # Store as .CSV files
    filename = f"{date_from}_{symbol}_{interval}.csv"
    df.to_csv(filename, index=True)

    return df

# Prepare historical data to train model
def prepare_data(symbol, date_from, date_to, interval='1D'):
    df = fetch_data(symbol, date_from, date_to, interval)
    # print(df.tail())
    df = calculate_indicators(df)
    return df

def uploading_hdata(training_data):
    client = pymongo.MongoClient(os.getenv('MONGO_URI'))
    db = client[os.getenv('DATABASE_NAME')]
    collection = db[os.getenv('TRAINING_DATA')]

    try:
        collection.insert_many(training_data)
    except Exception as e:
        print(f"An error occurred: {e}")

# Sample Test 
symbol = 'NVDA'
date_from = '2023-10-01'
date_to = '2024-10-01'
interval = '1H'

df = prepare_data(symbol, date_from, date_to, interval)
print("Successfully uploaded data!")