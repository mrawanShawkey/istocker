import os
import pickle
import pandas as pd
from collections import Counter
from config.paths import FEATURE_CACHE_DIR as FEATURE_DIR

feature_counts = Counter()
total_folds = 0

# ---------------------------------------------------------
# Load all fold feature files
# ---------------------------------------------------------
for file in os.listdir(FEATURE_DIR):

    if file.endswith(".pkl"):

        path = os.path.join(FEATURE_DIR, file)

        with open(path, "rb") as f:
            features = pickle.load(f)

        feature_counts.update(features)
        total_folds += 1

# ---------------------------------------------------------
# Convert to DataFrame
# ---------------------------------------------------------
df = pd.DataFrame({
    "feature": list(feature_counts.keys()),
    "count": list(feature_counts.values())
})

df["frequency"] = df["count"] / total_folds
df = df.sort_values("frequency", ascending=False)

print("\n============================")
print("FEATURE STABILITY")
print("============================")
print(df.head(20))

# Save results
df.to_csv("data/ml_data/features/feature_stability.csv", index=False)