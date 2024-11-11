import os
from datetime import datetime, timedelta
import pymongo
import pandas as pd
from dotenv import load_dotenv
from benzinga import financial_data
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataFetcher:
    def __init__(self):
        load_dotenv()
        self.mongo_uri = os.getenv('MONGO_URI')
        self.db_name = os.getenv('DATABASE_NAME')
        self.training_data_collection = os.getenv('TRAINING_DATA')
        self.fin = financial_data.Benzinga(os.getenv('BENZINGA_APIKEY'))
    
    def fetch_data(self, symbol, interval='1D'):
        try:
            start_date = (datetime.now() - timedelta(days=383)).strftime('%Y-%m-%d')
            current_date = datetime.now().strftime('%Y-%m-%d')
            data = self.fin.bars(symbol, start_date, current_date, interval)
            candles = data[0]['candles']
            df = pd.DataFrame(candles)
            
            # Store in "Historical Data" Collection
            data_dict = df.to_dict(orient="records")
            self.upload_historical_data(data_dict)
            logging.info(f"Fetched data for {symbol}")
            
            
            self.upload_recent_data(symbol, df.tail(26))  # Upload the most recent 26 days of data
            logging.info(f"Uploaded the most recent 26 days of data for {symbol} to the {symbol}_26 collection")
            
            return df
        except Exception as e:
            logging.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_indicators(self, df):
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
        except Exception as e:
            logging.error(f"Error calculating indicators: {e}")
        
        return df
    
    def upload_historical_data(self, training_data):
        try:
            client = pymongo.MongoClient(self.mongo_uri)
            db = client[self.db_name]
            collection = db[self.training_data_collection]

            # Clear the collection and upload new data
            try:
                collection.delete_many({})
                collection.insert_many(training_data)
                logging.info("Uploaded historical data to MongoDB")
            except Exception as e:
                logging.error(f"Error uploading data to MongoDB: {e}")
        except Exception as e:
            logging.error(f"Error connecting to MongoDB: {e}")
            
    def upload_recent_data(self, symbol, recent_data):
        try:
            client = pymongo.MongoClient(self.mongo_uri)
            db = client[self.db_name]
            collection_name = f"{symbol}-26"
            collection = db[collection_name]
            
            # Clean up the collection
            collection.delete_many({})  
            
            # Insert the recent 26 days of data
            recent_data_dict = recent_data.to_dict(orient="records")
            collection.insert_many(recent_data_dict)
            logging.info(f"Uploaded recent 26 days of data to {collection_name} collection.")
        except Exception as e:
            logging.error(f"Error uploading recent data to {symbol}_26: {e}")
    
    def prepare_data(self, symbol, interval='1D'):
        try:
            df = self.fetch_data(symbol, interval)
            if df.empty:
                logging.warning(f"No data fetched for {symbol}")
                return df
            df = self.calculate_indicators(df)
            logging.info(f"Prepared data for {symbol}")
            return df
        except Exception as e:
            logging.error(f"Error preparing data for {symbol}: {e}")
            return pd.DataFrame()

    def get_past_data(self, symbol):
        client = pymongo.MongoClient(self.mongo_uri)
        db = client[self.db_name]
        collection = db[f"{symbol}-26"]

        try:
            data = collection.find()
            df = pd.DataFrame(list(data))
            if not df.empty:
                logging.info(f"Fetched Data: \n{df.head(5)}")
            else:
                logging.warning("No data found within the specified date range.")
            return df
        except Exception as e:
            logging.error(f"Error fetching past data: {e}")
            return pd.DataFrame()

# Example usage
# if __name__ == "__main__":
#     data_fetcher = DataFetcher()
#     df = data_fetcher.prepare_data('AAPL')
#     print(df)