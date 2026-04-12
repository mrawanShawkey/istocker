import numpy as np
import pandas as pd

class WalkForwardSplit:
    """
    Walk-forward validation for panel time-series data.
    Splits are based on unique trading dates to avoid
    counting multiple assets as separate time steps.
    """

    def __init__(
        self,
        train_window=252 * 5,   # 5 years
        gap=252,                # purge gap
        test_window=252,        # 1 year test
        step=252                # move forward yearly
    ):
        self.train_window = train_window
        self.gap = gap
        self.test_window = test_window
        self.step = step

    def split(self, df):

        dates = np.array(sorted(df["date"].unique()))
        n_dates = len(dates)

        folds = []
        fold_records = []

        end_train = self.train_window

        while True:

            start_gap = end_train
            end_gap = start_gap + self.gap

            start_test = end_gap
            end_test = start_test + self.test_window

            if end_test > n_dates:
                break

            train_dates = dates[:end_train]
            test_dates = dates[start_test:end_test]

            train_idx = df.index[df["date"].isin(train_dates)].to_numpy()
            test_idx = df.index[df["date"].isin(test_dates)].to_numpy()

            folds.append((train_idx, test_idx))

            fold_records.append({
            "fold": len(folds),
            "train_start": train_dates[0],
            "train_end": train_dates[-1],
            "test_start": test_dates[0],
            "test_end": test_dates[-1],
        })
            end_train += self.step

        fold_info = pd.DataFrame(fold_records)
        return folds ,fold_info