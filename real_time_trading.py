import asyncio
import joblib
import logging
import os
import pandas as pd
import requests
import time
from benzinga import financial_data
from datetime import datetime
from dotenv import load_dotenv
from train_model import TradingModel
from trade_logs import log_trade
from fetch_load_mongo import DataFetcher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RealTimeTrader:
    def __init__(self, symbol, poll_interval=5, initial_funds=10000.0,
                 inventory=10, buying_power=10):
        load_dotenv()
        self.symbol = symbol
        self.api_key = os.getenv('BENZINGA_APIKEY')
        self.poll_interval = poll_interval
        self.initial_funds = initial_funds
        self.inventory = inventory
        self.buying_power = buying_power
        self.model = joblib.load('random_forest_model.joblib')
        self.base_url = "https://api.benzinga.com/api/v1/quoteDelayed"
        self.trading_model = TradingModel()
        # self.data_fetcher = DataFetcher()

        data_fetcher = DataFetcher()
        self.past_data = data_fetcher.get_past_data(self.symbol)
        
    def market_open(self):
        now = datetime.now()
        current_day = now.weekday()
        
        if current_day >= 0 and current_day <= 4 and 9 <= now.hour < 17:
            logging.info(f"Market is open: {now}")
            return True
            
        logging.info("Market is closed.")
        return False

    def fetch_latest_data(self):
        querystring = {
            "token": self.api_key,
            "symbols": self.symbol
        }
        headers = {"accept": "application/json"}
        
        try:
            response = requests.get(self.base_url, headers=headers, params=querystring)
            if response.status_code == 200:
                data = response.json()
                quotes = data["quotes"][0]["quote"]
            
                extracted_data = {
                    "time": quotes.get('date'),
                    "open": quotes.get('open'),
                    "high": quotes.get('high'),
                    "low": quotes.get('low'),
                    "close": quotes.get('last'), 
                    "volume": quotes.get('volume'),
                    "dateTime": quotes.get('previousCloseDate') 
                }
                
                logging.info(f"Fetched and extracted data: {extracted_data}")
                return pd.DataFrame([extracted_data])
                return
            else:
                logging.error(f"Failed to fetch data. Status code: {response.status_code}, Response: {response.text}")
                return pd.DataFrame()
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while fetching data: {e}")
            return pd.DataFrame()

    def trade_decision(self, prediction):
        if prediction == 1 or prediction == 2:
            return "buy"
        elif prediction == -1 or prediction == -2:
            return "sell"
        return ""

    def log_trade_action(self, trade_type, fetched_price, trade_price):
        log_trade(
            datetime.now(), self.symbol, self.initial_funds, fetched_price, 
            trade_price, self.inventory, self.buying_power, trade_type
        )

    async def perform_trading(self):
        while self.market_open():
            try:
                latest_data = self.fetch_latest_data()
                print("Successfully fetched latest data")
                
                if latest_data.empty:
                    logging.error("No data fetched, skipping this iteration.")
                    continue
                
                logging.info("Fetched latest data")
                fetched_price = latest_data["open"].iloc[0]
                
                # latest_data.drop_duplicates(subset='time', keep='last', inplace=True)
                # logging.info("Dropped duplicates from latest data")

                # if self.past_data.empty:
                #     self.past_data = latest_data
                #     logging.info("Initialized DataFrame with latest data")
                # else:

                local_df = pd.concat([self.past_data, latest_data]).drop_duplicates(subset='time', keep='last')
                logging.info("Updated DataFrame with latest data")

                local_df_TI = self.trading_model.calculate_indicators(local_df)
                logging.info("Calculated indicators")

                if len(local_df_TI) >= 26:
                    latest_row = local_df_TI.iloc[-1].copy()
                    logging.info("Sufficient data for indicators")
                    
                    X_real_time = pd.DataFrame({
                        'macd': [latest_row['macd']],
                        'macd_hist': [latest_row['macd_hist']],
                        'rsi': [latest_row['rsi']],
                        'slowk': [latest_row['slowk']],
                        'slowd': [latest_row['slowd']]
                    })
                    logging.info("Prepared data for prediction")
                    
                    prediction = self.model.predict(X_real_time)[0]
                    logging.info(f"Made prediction: {prediction}")
                    trade_type = self.trade_decision(prediction)
                    logging.info(f"Trade decision: {trade_type}")

                    # if trade_type:
                    trade_price = latest_data["open"].iloc[0]
                    self.log_trade_action(trade_type, fetched_price, trade_price)
                    logging.info(f"Logged trade action: {trade_type}")

            except Exception as e:
                logging.error(f"Error raised during real-time trading: {e}")

            time.sleep(self.poll_interval)
            logging.info("Sleeping for poll interval\n\n")

if __name__ == "__main__":
    trader = RealTimeTrader('AAPL')
    asyncio.run(trader.perform_trading())
