import os
import pymongo
import joblib
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
from benzinga import financial_data
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, mean_squared_error
import time

load_dotenv()

def fetch_data():
    """
    Fetch data from MongoDB and return it as a pandas DataFrame.
    Returns:
        pd.DataFrame: DataFrame containing the fetched data.
    """
    client = pymongo.MongoClient(os.getenv('MONGO_URI'))
    db = client[os.getenv('DATABASE_NAME')]
    collection = db[os.getenv('TRAINING_DATA')]

    try:
        data = collection.find()
        df = pd.DataFrame(list(data))
        if not df.empty:
            print(df.head(5))
        else:
            print("No data found within the specified date range.")
        return df
    except Exception as e:
        print(f"Error fetching data from MongoDB: {e}")
        return pd.DataFrame()

def prepare_labels(df, future_period=2, threshold=0.05):
    """
    Prepare labels for the dataset based on future price changes.
    Args:
        df (pd.DataFrame): DataFrame containing the data.
        future_period (int): Number of periods to shift for future price.
        threshold (float): Threshold for determining price change signals.
    Returns:
        pd.DataFrame: DataFrame with added 'future_price', 'price_change', and 'signal' columns.
    """
    
    df['future_price'] = df['close'].shift(-future_period)
    df['price_change'] = (df['future_price'] - df['close']) / df['close']

    print("Top 5 Rows:", df['close'].head(5), df['future_price'].head(5))

    df['signal'] = 0
    df.loc[df['price_change'] > threshold, 'signal'] = 1
    df.loc[(df['price_change'] < 0) & (df['signal'].shift(1) == 1), 'signal'] = -1
    df.loc[df['price_change'] < -threshold, 'signal'] = -2
    df.loc[(df['price_change'] > 0) & (df['signal'].shift(1) == -2), 'signal'] = 2

    df.dropna(inplace=True)
    print("Successfully added the signal column")
    return df

def calculate_indicators(df):
    """
    Calculate technical indicators for the dataset.
    Args:
        df (pd.DataFrame): DataFrame containing the data.
    Returns:
        pd.DataFrame: DataFrame with added technical indicator columns.
    """
    
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

def prepare_features_and_labels(df):
    """
    Prepare features and labels for model training.
    Args:
        df (pd.DataFrame): DataFrame containing the data.
    Returns:
        tuple: Tuple containing features (X) and labels (y).
    """
    
    df = prepare_labels(df)
    features = ['macd', 'macd_hist', 'rsi', 'slowk', 'slowd']
    label = 'signal'
    X = df[features]
    y = df[label]
    print("Prepared the features and labels")
    return X, y

def train_model(X, y):
    """
    Train a RandomForestClassifier model.
    Args:
        X (pd.DataFrame): DataFrame containing the features.
        y (pd.Series): Series containing the labels.
    Returns:
        RandomForestClassifier: Trained RandomForestClassifier model.
    """
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1234)
    model = RandomForestClassifier(criterion='entropy', n_estimators=100, max_depth=7, max_features=20)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)
    return model

def create_model():
    """
    Create and save a RandomForestClassifier model.
    """
    try:
        df = fetch_data()
        if df.empty:
            print("No data to train the model.")
            return
        df.drop(df.columns[0], axis=1, inplace=True)    
        df = calculate_indicators(df)
        X, y = prepare_features_and_labels(df)
        model = train_model(X, y)
        joblib.dump(model, 'random_forest_model.joblib')
        print("Model successfully created")
        
    except Exception as e:
        print(f"Error has occurred when creating model: {e}")

create_model()