from xgboost import XGBRegressor


class XGBoostModel:

    def __init__(self):

        # Initialize model ONCE per object
        self.model = XGBRegressor(
            n_estimators=250,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )

        self.is_fitted = False  # safety flag

    def fit(self, X, y):

        # Handle DataFrame input
        if hasattr(X, "columns"):
            if "symbol" in X.columns:
                X = X.drop(columns=["symbol"])

        # Fit model
        self.model.fit(X, y, verbose=False)

        # Mark as fitted
        self.is_fitted = True

    def predict(self, X):

        # Safety check
        if not self.is_fitted:
            raise ValueError("Model was not fitted before predict()")

        # Handle DataFrame input
        if hasattr(X, "columns"):
            if "symbol" in X.columns:
                X = X.drop(columns=["symbol"])

        return self.model.predict(X)