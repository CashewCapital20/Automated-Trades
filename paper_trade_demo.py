#! C:\Users\potat\Downloads\Automated-Trading\automated-trades-env\Scripts\python.exe

import os
import joblib
import pandas as pd
import numpy as np
import time
import random
from dotenv import load_dotenv
from datetime import datetime, timedelta
from benzinga import financial_data


load_dotenv()
TO_DATE = datetime.now().strftime('%Y-%m-%d')
FROM_DATE = '2024-01-01'

from_timestamp = int(datetime.strptime(FROM_DATE, '%Y-%m-%d').timestamp())
to_timestamp = int(datetime.strptime(TO_DATE, '%Y-%m-%d').timestamp())


# Run the model on a random date (5min candles) and see performace (e.g. ending balance)
def run_paper_trade(b, inv, qnt):
    print(b, inv, qnt)
    
    # Get a full-day (5 min candles) market data from Benzinga
    while True:
        d = random.randint(from_timestamp, to_timestamp)
        start_date = datetime.fromtimestamp(d)
        if start_date.weekday() >= 5:
            continue
        
        end_date = (start_date + timedelta(days=1)).strftime('%Y-%m-%d')
        start_date = start_date.strftime('%Y-%m-%d')
        
        print(f"Fetching data from {start_date} to {end_date}")
        
        fin = financial_data.Benzinga(os.getenv('API_KEY'))
        data = fin.bars('NVDA', start_date, end_date)
        
        if not data:
            print("No data fetched")
            time.sleep(1)
            continue
        else:
            print("Data fetched successfully")
            print(data)
            data = data[0]['candles']
            time.sleep(1)  # Cooldown period 
            
        break
    
    # d = random.randint(from_timestamp, to_timestamp)
    # start_date = datetime.fromtimestamp(d).strftime('%Y-%m-%d')
    # end_date = (datetime.fromtimestamp(d) + timedelta(days=1)).strftime('%Y-%m-%d')
    # fin = financial_data.Benzinga(os.getenv('API_KEY'))
    # data = fin.bars('GOOG', start_date, end_date, '1M')
    
    # print(data)
    model = joblib.load('random_forest_model.joblib')
    predictation = model.predict(data)
    print(predictation)

        
BALANCE = 10000
INVENTORY = 10
QUANTITY = 50       # Buying and selling power

run_paper_trade(BALANCE, INVENTORY, QUANTITY)