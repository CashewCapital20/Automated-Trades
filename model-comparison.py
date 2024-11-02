from sklearn.ensemble import StackingRegressor, GradientBoostingRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, RidgeCV, LogisticRegression
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.svm import SVR, SVC
from sklearn.metrics import mean_squared_error, accuracy_score
from sklearn.model_selection import train_test_split

# Prepare data (use the prepare_features_and_labels function to get X, y)
X, y = prepare_features_and_labels(df_one_stock)  # Replace df_one_stock with your DataFrame

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
