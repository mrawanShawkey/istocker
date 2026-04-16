import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


class SARIMAXModel:
    """
    Fast benchmark SARIMAX model for the walk-forward pipeline.

    Notes:
    - This is intentionally simplified for speed and stability.
    - It is best used as a baseline / comparison model, not the main model.
    """

    def __init__(
        self,
        order=(1, 0, 0),
        max_features=8,
        maxiter=50,
        trend="n",
    ):
        self.order = order
        self.max_features = max_features
        self.maxiter = maxiter
        self.trend = trend

        self.model = None
        self.fitted_model = None
        self.train_len = None
        self.feature_names = None
        self.is_fitted = False

    def _to_dataframe(self, X):
        if isinstance(X, pd.DataFrame):
            return X.copy()
        return pd.DataFrame(X)

    def _clean(self, X, y=None):
        X = self._to_dataframe(X)

        # Drop non-numeric identifier columns if present
        for col in ["symbol", "date"]:
            if col in X.columns:
                X = X.drop(columns=[col])

        # Force numeric
        X = X.apply(pd.to_numeric, errors="coerce").astype(np.float32)

        # Fill missing values with train-time medians
        X = X.fillna(X.median(numeric_only=True))

        # Reduce dimensionality for speed/stability
        if self.feature_names is None:
            self.feature_names = list(X.columns[: self.max_features])
        X = X[self.feature_names].reset_index(drop=True)

        if y is None:
            return X

        y = pd.Series(y).copy()
        y = pd.to_numeric(y, errors="coerce").astype(np.float32).reset_index(drop=True)

        mask = y.notna() & X.notna().all(axis=1)
        X = X.loc[mask].reset_index(drop=True)
        y = y.loc[mask].reset_index(drop=True)

        return X, y

    def fit(self, X, y, symbols=None):
        X, y = self._clean(X, y)

        if len(y) < 30:
            raise ValueError("Not enough observations to fit SARIMAX.")

        self.train_len = len(y)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            self.model = SARIMAX(
                endog=y,
                exog=X,
                order=self.order,
                trend=self.trend,
                enforce_stationarity=False,
                enforce_invertibility=False,
                simple_differencing=False,
            )

            self.fitted_model = self.model.fit(
                disp=False,
                method="lbfgs",
                maxiter=self.maxiter,
            )

        self.is_fitted = True

    def predict(self, X, symbols=None):
        if not self.is_fitted:
            raise ValueError("SARIMAXModel must be fitted before predict().")

        X = self._clean(X)

        start = self.train_len
        end = self.train_len + len(X) - 1

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            forecast = self.fitted_model.predict(
                start=start,
                end=end,
                exog=X,
            )

        return np.asarray(forecast, dtype=np.float32)