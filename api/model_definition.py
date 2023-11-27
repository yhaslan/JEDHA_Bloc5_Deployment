from sklearn.svm import SVR
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler
import pandas as pd

class SVR_with_InverseScaler(BaseEstimator):
    def __init__(self, scaler=StandardScaler(), svr=SVR(kernel='rbf', C=1, degree=3, gamma='scale', epsilon=0.1)):
        self.scaler = scaler
        self.svr = svr

    def fit(self, X, y):
        y_scaled = self.scaler.fit_transform(y)  # Scale the target variable
        self.svr.fit(X, y_scaled.ravel())  # Fit the model with scaled target variable
        return self

    def predict(self, X):
        scaled_predictions = self.svr.predict(X)
        unscaled_predictions = self.scaler.inverse_transform(scaled_predictions.reshape(-1, 1)).flatten()
        return unscaled_predictions
    
