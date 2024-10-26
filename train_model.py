#! C:\Users\potat\Downloads\Automated-Trading\automated-trades-env\Scripts\python.exe

import os
import pymongo
import joblib
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime 
from benzinga import financial_data
# from sklearn.tree import DecisionTreeRegressor
# from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, mean_squared_error
# import time
# from sklearn.metrics import roc_curve
# from sklearn.metrics import auc

load_dotenv()
to_date = datetime.now().strftime('%Y-%m-%d')
from_date = '2024-01-01'

def export_training_data():
    # URI = os.getenv('MONGO_URI')
    # DB_NAME = os.getenv('DATABASE_NAME')
    # COLL_NAME = os.getenv('COLLECTION_NAME')

    # client = pymongo.MongoClient(URI)
    # db = client[DB_NAME]
    # collection = db[COLL_NAME]
    # data = collection.find()
    # print("Successfully exported training data")
    
    fin = financial_data.Benzinga(os.getenv('API_KEY'))
    data = fin.bars('FTV', from_date, to_date, '1D')
    # print(data)
    candles = data[0]['candles']
    df = pd.DataFrame(candles)
    print(df.head(5))
    return df

def prepare_labels(df, future_period=2, threshold=0.05):
    # Future price to compare with predicted price
    df['future_price'] = df['close'].shift(-future_period)
    # Percent change between future price and predicted price
    df['price_change'] = (df['future_price'] - df['close']) / df['close']

    # Create the label
    df['signal'] = 0
    df.loc[df['price_change'] > threshold, 'signal'] = 1    # buy signal
    df.loc[(df['price_change'] < 0) & (df['signal'].shift(1) == 1), 'signal'] = -1    # Sell signal
    df.loc[df['price_change'] < -threshold, 'signal'] = -2    # Short signal
    df.loc[(df['price_change'] > 0) & (df['signal'].shift(1) == -2), 'signal'] = 2    # Cover signal

    print("Successfully added the signal column")
    # Drop last rows with missing future price data
    return df

# Prepare the feature set and labels for training
def prepare_features_and_labels(df):
    df = prepare_labels(df)
    features = ['macd', 'macd_hist', 'rsi', 'slowk', 'slowd']
    label = 'signal'
    X = df[features]
    y = df[label]
    print("Prepared the features and labels")
    return X, y

def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1234)
    model = RandomForestClassifier(criterion='entropy', n_estimators=100, max_depth=7, max_features=20)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)
    return model

def create_model():
    df = export_training_data()
    df.drop(df.columns[0], axis=1, inplace=True)
    print(df.head(5))
    
    df = calculate_indicators(df)
    X, y = prepare_features_and_labels(df)
    model = train_model(X, y)
    joblib.dump(model, 'random_forest_model.joblib')
    print("Model successfully created")

create_model()