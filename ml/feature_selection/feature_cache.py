"""
feature_cache.py

Handles saving and loading selected features per fold.
"""

import os
import pickle

from config.paths import FEATURE_CACHE_DIR

def get_feature_path(fold_id):
    return os.path.join(FEATURE_CACHE_DIR, f"features_fold_{fold_id}.pkl")


def save_features(fold_id, features):
    os.makedirs(FEATURE_CACHE_DIR, exist_ok=True)

    path = get_feature_path(fold_id)

    with open(path, "wb") as f:
        pickle.dump(list(features), f)


def load_features(fold_id):

    path = get_feature_path(fold_id)

    if not os.path.exists(path):
        return None

    with open(path, "rb") as f:
        return pickle.load(f)