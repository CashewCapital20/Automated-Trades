#! C:\Users\potat\Downloads\Automated-Trading\automated-trades-env\Scripts\python.exe

import os
import joblib
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from train_model import TradingModel
from trade_logs import log_trade
from fetch_load_mongo import DataFetcher
from benzinga import financial_data
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

class PaperTrader:
    def __init__(self, symbol, initial_funds=10000.0, inventory=10, buying_power=10):
        self.symbol = symbol
        self.api_key = os.getenv('BENZINGA_APIKEY')
        self.initial_funds = initial_funds
        self.inventory = inventory
        self.buying_power = buying_power
        self.model = joblib.load('random_forest_model.joblib')
        self.trading_model = TradingModel()
        data_fetcher = DataFetcher()
        self.past_data = data_fetcher.get_past_data(self.symbol)

    def fetch_latest_historical_data(self, symbol):
        try:
            fin = financial_data.Benzinga(self.api_key)
            data = fin.bars(symbol, date_from='1d')
            candles = data[0]['candles']
            df = pd.DataFrame(candles)
            return df
        except Exception as e:
            logging.error(f"Error raised fetching latest historical data: {e}")

    def trade_decision(self, prediction):
        if prediction == 1 or prediction == 2:
            return "Buy"
        elif prediction == -1 or prediction == -2:
            return "Sell"
        return "Hold"

    def log_trade_action(self, trade_type, fetched_price, trade_price):
        log_trade(
            datetime.now(), self.symbol, self.initial_funds, fetched_price, 
            trade_price, self.inventory, self.buying_power, trade_type
        )

    def run_paper_trade(self):
        historical_data = self.fetch_latest_historical_data(self.symbol)
        if historical_data.empty:
            logging.error("No historical data fetched.")
            return
        
        # Store as 5-min candles
        for index, row in historical_data.iterrows():
            try:
                latest_data = pd.DataFrame([row])
                fetched_price = latest_data["open"].iloc[0]
                
                print("LATEST DATA: ", latest_data)
                # print("PRICE: ", fetched_price)

                local_df = pd.concat([self.past_data, latest_data]).drop_duplicates(subset='time', keep='last')
                local_df_TI = self.trading_model.calculate_indicators(local_df)                
                
                if len(local_df_TI) >= 26:
                    latest_row = local_df_TI.iloc[-1].copy()
                    X_real_time = pd.DataFrame({
                        'macd': [latest_row['macd']],
                        'macd_hist': [latest_row['macd_hist']],
                        'rsi': [latest_row['rsi']],
                        'slowk': [latest_row['slowk']],
                        'slowd': [latest_row['slowd']]
                    })

                    prediction = self.model.predict(X_real_time)[0]
                    trade_type = self.trade_decision(prediction)
                    
                    print(trade_type)

                    if trade_type != "Hold":
                        trade_price = latest_data["open"].iloc[0]
                        self.log_trade_action(trade_type, fetched_price, trade_price)
                        logging.info(f"Logged trade action: {trade_type}")

                time.sleep(1)
            except Exception as e:
                logging.error(f"Error raised during paper trading: {e}")

if __name__ == "__main__":
    paper_trader = PaperTrader('AAPL')
    paper_trader.run_paper_trade()