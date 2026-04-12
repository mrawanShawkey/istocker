import numpy as np
import pandas as pd
import warnings
from statsmodels.tsa.statespace.sarimax import SARIMAX


class SARIMAXModel:

    def __init__(self):
        self.model       = None
        self.fitted_model = None
        self.train_len   = None

    def _clean(self, X, y=None):

        X = X.copy()

        # ---------------------------------------------------------
        # Drop symbol first — SARIMAX needs numeric only
        # ---------------------------------------------------------
        if "symbol" in X.columns:
            X = X.drop(columns=["symbol"])

        # ---------------------------------------------------------
        # Force numeric
        # ---------------------------------------------------------
        X = X.apply(pd.to_numeric, errors="coerce").astype(float)
        X = X.fillna(X.median())
        X = X.reset_index(drop=True)

        if y is not None:
            y = pd.to_numeric(y, errors="coerce").astype(float)
            y = y.reset_index(drop=True)

            mask = y.notna() & X.notna().all(axis=1)

            y = y[mask].reset_index(drop=True)
            X = X[mask].reset_index(drop=True)

            return X, y

        return X

    def fit(self, X, y):fit

        X, y = self._clean(X, y)

        self.train_len = len(y)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            self.model = SARIMAX(
                endog=y,
                exog=X,
                order=(1, 0, 1),
                enforce_stationarity=False,
                enforce_invertibility=False
            )

            # Try multiple optimizers — fall back if one fails
            for method in ["lbfgs", "nm", "powell"]:
                try:
                    self.fitted_model = self.model.fit(
                        disp=False,
                        maxiter=500,
                        method=method
                    )
                    break
                except Exception:
                    continue

    def predict(self, X):

        X = self._clean(X)

        start = self.train_len
        end   = self.train_len + len(X) - 1

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            forecast = self.fitted_model.predict(
                start=start,
                end=end,
                exog=X
            )

        return forecast.values