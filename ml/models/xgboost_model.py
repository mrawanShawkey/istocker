from xgboost import XGBRegressor
import numpy as np

class XGBoostModel:

    def __init__(self,params=None):

        default_params = {
            "n_estimators": 500,
            "max_depth": 3,
            "learning_rate": 0.03,
            "subsample": 0.7,
            "colsample_bytree": 0.7,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "min_child_weight": 5,
            "random_state": 42,
            "eval_metric": "rmse",
            "early_stopping_rounds": 30
        }

        if params:
            default_params.update(params)

        self.model = XGBRegressor(**default_params)
        self.is_fitted = False
    
    def fit(self, X, y):
        if hasattr(X, "columns") and "symbol" in X.columns:
            X = X.drop(columns=["symbol"])

        # Time-ordered validation split — last 15% of training rows
        n = len(X)
        split = int(n * 0.85)
        X_tr, X_val = X[:split], X[split:]
        y_tr, y_val = y[:split], y[split:]

        self.model.fit(
            X_tr, y_tr,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        self.is_fitted = True

    def predict(self, X):
        if not self.is_fitted:
            raise ValueError("Model was not fitted before predict()")
        if hasattr(X, "columns") and "symbol" in X.columns:
            X = X.drop(columns=["symbol"])
        return self.model.predict(X)