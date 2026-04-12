import pandas as pd
import numpy as np

from sklearn.feature_selection import mutual_info_regression
from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor


class FeatureSelector:

    def __init__(
        self,
        corr_threshold=0.90,
        mi_top_k=20,
        lasso_alpha=0.01,
        bootstrap_runs=30,
        stability_threshold=0.6,
        maxiters=10000
    ):

        self.corr_threshold = corr_threshold
        self.mi_top_k = mi_top_k
        self.lasso_alpha = lasso_alpha
        self.bootstrap_runs = bootstrap_runs
        self.stability_threshold = stability_threshold
        self.maxiters = maxiters

        self.selected_features = None


    # ---------------------------------------------------
    # Step 1 — Correlation Filtering
    # ---------------------------------------------------

    def correlation_filter(self, X, y):

        corr_matrix = X.corr().abs()

        upper_triangle = corr_matrix.where(
            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
        )

        dropped_features = set()

        for col in upper_triangle.columns:

            high_corr = upper_triangle.index[
                upper_triangle[col] > self.corr_threshold
            ].tolist()

            for row in high_corr:

                if row in dropped_features or col in dropped_features:
                    continue

                corr_row = abs(np.corrcoef(X[row], y)[0, 1])
                corr_col = abs(np.corrcoef(X[col], y)[0, 1])

                if corr_row > corr_col:
                    dropped_features.add(col)
                else:
                    dropped_features.add(row)

        X_filtered = X.drop(columns=list(dropped_features))

        return X_filtered


    # ---------------------------------------------------
    # Step 2 — Mutual Information Ranking
    # ---------------------------------------------------

    def mutual_information_filter(self, X, y):

        mi = mutual_info_regression(X, y)

        mi_scores = pd.Series(mi, index=X.columns)

        mi_scores = mi_scores.sort_values(ascending=False)

        selected = mi_scores.head(self.mi_top_k).index.tolist()

        return X[selected]


    # ---------------------------------------------------
    # Step 3 — LASSO Stability Selection
    # ---------------------------------------------------

    def lasso_selection(self, X, y):

        scaler = StandardScaler()

        X_scaled = scaler.fit_transform(X)

        feature_counts = np.zeros(X.shape[1])

        for _ in range(self.bootstrap_runs):

            sample_idx = np.random.choice(len(X), len(X), replace=True)

            X_sample = X_scaled[sample_idx]
            y_sample = y.iloc[sample_idx]

            model = Lasso(alpha=self.lasso_alpha , max_iter=self.maxiters)

            model.fit(X_sample, y_sample)

            selected = np.abs(model.coef_) > 1e-5

            feature_counts += selected

        stability_scores = feature_counts / self.bootstrap_runs

        stability_scores = pd.Series(stability_scores, index=X.columns)

        selected_features = stability_scores[
            stability_scores >= self.stability_threshold
        ].index.tolist()

        return selected_features

    # ---------------------------------------------------
    # Step 4 — tree importance validation
    # ---------------------------------------------------

    def tree_importance_validation(self, X, y, threshold=0.01):

        model = XGBRegressor(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )

        model.fit(X, y)

        importances = pd.Series(
            model.feature_importances_,
            index=X.columns
        )

        self.tree_importance_scores = importances.sort_values(ascending=False)

        selected_features = importances[importances > threshold].index.tolist()

        self.selected_features = selected_features

        return X[selected_features]


    # ---------------------------------------------------
    # Full Pipeline
    # ---------------------------------------------------

    def fit(self, X, y):

        # Step 1
        X = self.correlation_filter(X, y)

        # Step 2
        X = self.mutual_information_filter(X, y)

        # Step 3
        self.selected_features = self.lasso_selection(X, y)

        # Step 4
        X = self.tree_importance_validation(X, y)

        return self.selected_features


    def transform(self, X):

        if self.selected_features is None:
            raise ValueError("FeatureSelector must be fitted first.")

        return X[self.selected_features]


    def fit_transform(self, X, y):

        self.fit(X, y)

        return self.transform(X)