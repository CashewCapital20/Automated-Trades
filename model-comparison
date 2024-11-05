from sklearn.ensemble import StackingRegressor, GradientBoostingRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, RidgeCV, LogisticRegression
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.svm import SVR, SVC
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report 
from sklearn.model_selection import train_test_split
from train_model import prepare_features_and_labels

from benzinga import financial_data
import pandas as pd

API_KEY = "060fc707469a4680bec4894e5ce0ca7a"
MONGO_URI = "mongodb+srv://testUser:ydenWcQc9CdCD7L9@automated-trades.nhwk8.mongodb.net/?retryWrites=true&w=majority&appName=Automated-Trades"
DATABASE_NAME = "Benzinga"
TRAINING_DATA = "Historical Data"
MARKET_LOG = "Market Logs"

def fetch_data(symbol, date_from, date_to, interval='1D'):
    try:
        fin = financial_data.Benzinga(API_KEY)
        data = fin.bars(symbol, date_from, date_to, interval)
        candles = data[0]['candles']
        df = pd.DataFrame(candles)
        
        # Store in "Historical Data" Collection
        data = df.to_dict(orient="records")
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

# Sample Test 
symbol = 'NVDA'
date_from = '2023-10-01'
date_to = '2024-10-27'
interval = '1D'

df = prepare_data(symbol, date_from, date_to, interval)

# Prepare data (use the prepare_features_and_labels function to get X, y)
X, y = prepare_features_and_labels(df.dropna())  # Replace df_one_stock with your DataFrame

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Regression models
def regression_models(X_train, X_test, y_train, y_test):
    models = {
        'Stacking Regressor': StackingRegressor(estimators=[("DT", GradientBoostingRegressor()), ("LR", LinearRegression())]),
        'Gradient Boosting': GradientBoostingRegressor(max_depth=4, n_estimators=300),
        'Ridge Regression': RidgeCV(alphas=(0.1, 1.0, 10.0)),
        'KNN Regressor': KNeighborsRegressor(n_neighbors=5),
        'Support Vector Regressor': SVR(kernel='rbf')
    }
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        rmse = mean_squared_error(y_test, y_pred, squared=False)
        print(f"{name} - RMSE: {rmse:.3f}")

# Classification models
def classification_models(X_train, X_test, y_train, y_test):
    models = {
        'Random Forest': RandomForestClassifier(criterion='entropy', n_estimators=100),
        'Logistic Regression': LogisticRegression(max_iter=1000),
        'Support Vector Classifier': SVC(kernel='linear'),
        'KNN Classifier': KNeighborsClassifier(n_neighbors=5)
    }
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"{name} - Accuracy: {accuracy:.3f}")

# Run both comparisons
print("Regression Model Comparison:")
regression_models(X_train, X_test, y_train, y_test)

print("\nClassification Model Comparison:")
classification_models(X_train, X_test, y_train, y_test)
