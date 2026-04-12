import pandas as pd
from pathlib import Path
import sys
ROOT_DIR = Path().resolve().parents[1]
sys.path.append(str(ROOT_DIR))
from config.paths import CLEANED_MARKET_FILE, MACRO_FILE, MACROECNOMIC_ALIGNMENT_FILE 


class MacroAligner:

    def __init__(self,
                market_file=CLEANED_MARKET_FILE,
                macro_file=MACRO_FILE):
        self.market_file = market_file
        self.macro_file = macro_file
        self.market_df = None
        self.macro_df = None

    def load(self):
        self.market_df = pd.read_csv(self.market_file)
        self.macro_df = pd.read_excel(self.macro_file)

        # Ensure date column exists
        self.market_df['date'] = pd.to_datetime(self.market_df['date'])


        # Explicit engine to avoid format errors
        self.macro_df = pd.read_excel(
            self.macro_file,
            engine="openpyxl"
        )

        # Standardize macro columns
        self.macro_df.columns = (
            self.macro_df.columns
                .str.strip()
                .str.lower()
                .str.replace(" ", "_")
        )

        # Remove empty unnamed columns
        self.macro_df = self.macro_df.loc[:, ~self.macro_df.columns.str.contains('^unnamed')]

        # Convert year to integer
        self.macro_df['year'] = pd.to_numeric(self.macro_df['year'], errors='coerce')

        # Convert market date
        self.market_df['date'] = pd.to_datetime(self.market_df['date'])

    def align(self):
        # Extract year from trading date
        self.market_df['year'] = self.market_df['date'].dt.year

        # Apply 1-year lag (critical to avoid look-ahead bias)
        self.market_df['macro_year'] = self.market_df['year'] - 1

        # Merge macro
        merged = self.market_df.merge(
            self.macro_df,
            left_on='macro_year',
            right_on='year',
            how='left'
        )

        # Clean redundant merge column
        merged.drop(columns=['year_y'], inplace=True, errors='ignore')
        merged.rename(columns={'year_x': 'year'}, inplace=True)

        self.aligned_df = merged

        print("Macro alignment completed.")
        print("Rows:", len(self.aligned_df))

        return self.aligned_df

    def save(self, output_path=MACROECNOMIC_ALIGNMENT_FILE):
        output_path.parent.mkdir(parents=True, exist_ok=True)   
        self.aligned_df.to_csv(output_path, index=False)
        print(f"Saved aligned dataset to {output_path}")


if __name__ == "__main__":
    aligner = MacroAligner()
    aligner.load()
    aligner.align()
    aligner.save()
    df = pd.read_csv(MACROECNOMIC_ALIGNMENT_FILE)
    print(df[['date','gdp','inflation_rate','interest_rate']].head())
    print(aligner.macro_df.head())
    print(aligner.macro_df.columns)
