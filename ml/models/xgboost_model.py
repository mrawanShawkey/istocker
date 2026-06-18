from xgboost import XGBRegressor
import numpy as np


class XGBoostModel:

    def __init__(self, params=None, validation_fraction=0.15):

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
            "early_stopping_rounds": 30,
            "objective": "reg:squarederror",
            "tree_method": "hist",
            "n_jobs": -1,
        }

        if params:
            default_params.update(params)

        self.model = XGBRegressor(**default_params)
        self.is_fitted = False
        self.validation_fraction = validation_fraction

    def fit(self, X, y):
        if hasattr(X, "columns") and "symbol" in X.columns:
            X = X.drop(columns=["symbol"])

        X = np.asarray(X)
        y = np.asarray(y)

        n = len(X)

        if n < 50:
            self.model.fit(X, y, verbose=False)
            self.is_fitted = True
            return self

        split = int(n * (1 - self.validation_fraction))

        X_tr, X_val = X[:split], X[split:]
        y_tr, y_val = y[:split], y[split:]

        self.model.fit(
            X_tr,
            y_tr,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )

        self.is_fitted = True
        return self

    def predict(self, X):
        if not self.is_fitted:
            raise ValueError("Model was not fitted before predict()")

        if hasattr(X, "columns") and "symbol" in X.columns:
            X = X.drop(columns=["symbol"])

        X = np.asarray(X)

        return self.model.predict(X)