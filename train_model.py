import os
import pymongo
import joblib
import pandas as pd
from dotenv import load_dotenv
from benzinga import financial_data
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TradingModel:
    def __init__(self):
        load_dotenv()
        self.mongo_uri = os.getenv('MONGO_URI')
        self.db_name = os.getenv('DATABASE_NAME')
        self.training_data_collection = os.getenv('TRAINING_DATA')
        self.fin = financial_data.Benzinga(os.getenv('API_KEY'))
    
    def fetch_data(self):
        """
        Fetch data from MongoDB and return it as a pandas DataFrame.
        """
        client = pymongo.MongoClient(self.mongo_uri)
        db = client[self.db_name]
        collection = db[self.training_data_collection]

        try:
            data = collection.find()
            df = pd.DataFrame(list(data))
            if not df.empty:
                logging.info(f"Fetched Data: \n{df.head(5)}")
            else:
                logging.warning("No data found within the specified date range.")
            return df
        except Exception as e:
            logging.error(f"Error fetching data from MongoDB: {e}")
            return pd.DataFrame()

    def prepare_labels(self, df, future_period=2, threshold=0.05):
        df['future_price'] = df['close'].shift(-future_period)
        df['price_change'] = (df['future_price'] - df['close']) / df['close']
        
        logging.info(f"Top 5 Rows:\n{df['close'].head(5)}")

        df['signal'] = 0
        
        # buy signal
        df.loc[df['price_change'] > threshold, 'signal'] = 1
        # sell signal
        df.loc[(df['price_change'] < 0) & (df['signal'].shift(1) == 1), 'signal'] = -1
        # strong sell signal
        df.loc[df['price_change'] < -threshold, 'signal'] = -2
        # re-entry buy signal
        df.loc[(df['price_change'] > 0) & (df['signal'].shift(1) == -2), 'signal'] = 2

        df.dropna(inplace=True)
        logging.info("Successfully added the signal column")
        return df

    def calculate_indicators(self, df):
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

    def prepare_features_and_labels(self, df):
        df = self.prepare_labels(df)
        features = ['macd', 'macd_hist', 'rsi', 'slowk', 'slowd']
        label = 'signal'
        X = df[features]
        y = df[label]
        logging.info("Prepared the features and labels")
        return X, y

    def train_model(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1234)
        model = RandomForestClassifier(criterion='entropy', n_estimators=100, max_depth=7, max_features=20)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logging.info(f"Model accuracy: {accuracy}")
        return model

    def create_model(self):
        """
        Create and save a RandomForestClassifier model.
        """
        try:
            df = self.fetch_data()
            if df.empty:
                logging.warning("No data to train the model.")
                return
            df.drop(df.columns[0], axis=1, inplace=True)    
            df = self.calculate_indicators(df)
            X, y = self.prepare_features_and_labels(df)
            model = self.train_model(X, y)
            joblib.dump(model, 'random_forest_model.joblib')
            logging.info("Model successfully created")
        except Exception as e:
            logging.error(f"Error has occurred when creating model: {e}")

# Example usage
# if __name__ == "__main__":
#     trading_model = TradingModel()
#     trading_model.create_model()