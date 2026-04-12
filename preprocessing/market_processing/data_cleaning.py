import pandas as pd
from pathlib import Path
import sys
ROOT_DIR = Path().resolve().parents[1]
sys.path.append(str(ROOT_DIR))
from config.paths import RAW_MARKET_FILE, CLEANED_MARKET_FILE

class MarketDataCleaner:

    def __init__(self, filepath=RAW_MARKET_FILE):
        self.filepath = filepath
        self.df = None

    def load(self):
        self.df = pd.read_csv(self.filepath)

    def clean(self):

        initial_rows = len(self.df)

        # Standardize column names
        self.df.columns = (
            self.df.columns
                .str.strip()        # remove leading/trailing spaces
                .str.lower()        # lowercase
                .str.replace(" ", "_")  # replace spaces with underscore
        )

        # Convert date
        self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')

        # Remove rows with invalid dates
        self.df = self.df[self.df['date'].notna()]

        # Sort properly
        self.df = self.df.sort_values(['symbol', 'date']).reset_index(drop=True)

        # Drop duplicates
        self.df = self.df.drop_duplicates()

        # Drop redundant column
        if 'ticker' in self.df.columns:
            self.df = self.df.drop(columns=['ticker'])

        # Ensure numeric
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        self.df[numeric_cols] = self.df[numeric_cols].apply(pd.to_numeric, errors='coerce')

        # Remove rows with NaNs in critical columns
        self.df = self.df.dropna(subset=numeric_cols)

        # Remove non-positive prices
        self.df = self.df[self.df['close'] > 0]

        final_rows = len(self.df)

        print(f"Cleaning completed: {initial_rows} → {final_rows} rows")

        return self.df

    def save(self, output_path=CLEANED_MARKET_FILE):
        self.df.to_csv(output_path, index=False)

if __name__ == "__main__":
    cleaner = MarketDataCleaner()
    cleaner.load()
    cleaner.clean()
    cleaner.save()