import numpy as np


def directional_accuracy(y_true, y_pred):
    """
    Percentage of predictions where the sign is correct.
    """
    return np.mean(np.sign(y_true) == np.sign(y_pred))


def information_coefficient(y_true, y_pred):
    """
    Computes the Pearson correlation between predicted
    and actual returns.

    If variance of predictions or targets is zero,
    return 0 to avoid NaN issues.
    """

    if np.std(y_pred) == 0 or np.std(y_true) == 0:
        return 0

    return np.corrcoef(y_true, y_pred)[0, 1]


def out_of_sample_r2(y_true, y_pred, train_mean):
    """
    Out-of-sample R² relative to historical mean benchmark.
    """

    sse_model = np.sum((y_true - y_pred) ** 2)
    sse_benchmark = np.sum((y_true - train_mean) ** 2)

    return 1 - (sse_model / sse_benchmark)