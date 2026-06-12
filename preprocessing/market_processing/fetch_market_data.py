from tvDatafeed import TvDatafeed, Interval
from pathlib import Path
import time
import sys
import glob
import yfinance as yf
import pandas as pd

# Setup project directories cleanly
ROOT_DIR = Path().resolve()
sys.path.append(str(ROOT_DIR))
from config.paths import MARKET_DIR

EGX30_TICKERS = [
    'COMI', 'HRHO', 'TMGH', 'FWRY', 'EAST', 'SWDY', 'ABUK',
    'AMOC', 'CCAP', 'ESRS', 'HELI', 'ORHD', 'PHDC', 'ETEL',
    'MTIE', 'CIEB', 'EXPA', 'BTFH', 'ORWE', 'MASR', 'SUGR',
    'ISPH', 'VLMR', 'CIRA', 'JUFO', 'DOMT', 'MFPC', 'EGAL',
    'ADIB', 'EFIC'
]

def fetch_tv_data(tv, n_bars, purpose, tickers=EGX30_TICKERS):
    """Fetch historical data from TradingView for a list of tickers."""
    for ticker in tickers:
        print(f"Fetching data from TradingView: {ticker} ...")
        if purpose == 'ml':
            file_path = MARKET_DIR / 'raw' / f"{ticker}_TV_Data.csv"
        if purpose == 'daily':
            file_path = MARKET_DIR / 'daily' / f"{ticker}_TV_Data.csv"
        if file_path.exists():
            print(f"Skipping {ticker}... File already exists.")
            continue
        try:
            df = tv.get_hist(symbol=ticker, exchange='EGX', interval=Interval.in_daily, n_bars=n_bars)
            if df is not None and not df.empty:
                # Standardize dates right away
                df = df.reset_index()
                if 'datetime' in df.columns:
                    df = df.rename(columns={'datetime': 'date'})
                    df['date'] = df['date'].dt.date
                
                df.to_csv(file_path, index=True)
            else:
                print(f"Warning: No data returned for {ticker}")
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
        time.sleep(1)


def fetch_with_retries(tv, tickers, n_bars=5000, retries=3, delay_between_attempts=3, post_delay=2):
    """Attempt to fetch tickers with retry logic and reconnect on failure."""
    for ticker in tickers:
        print(f"Fetching data with retries: {ticker} ...")
        success = False
        attempts_left = retries

        while not success and attempts_left > 0:
            try:
                df = tv.get_hist(symbol=ticker, exchange='EGX', interval=Interval.in_daily, n_bars=n_bars)
                if df is not None and not df.empty:
                    df = df.reset_index()
                    if 'datetime' in df.columns:
                        df = df.rename(columns={'datetime': 'date'})
                        df['date'] = df['date'].dt.date
                        
                    df.to_csv(MARKET_DIR / 'raw' / f"{ticker}_TV_Data.csv", index=False)
                    print(f" Successfully fetched {ticker}.")
                    success = True
                else:
                    attempt_num = retries - attempts_left + 1
                    print(f"No data for {ticker} on attempt {attempt_num}...")
                    attempts_left -= 1
                    time.sleep(delay_between_attempts)

            except Exception as e:
                print(f"Connection error for {ticker}: {e}; reconnecting client...")
                tv = TvDatafeed()
                attempts_left -= 1
                time.sleep(delay_between_attempts)

        time.sleep(post_delay)


# def fetch_ekhoa_from_yahoo(output_filename=MARKET_DIR / 'raw' / 'EKHOA_TV_Data.csv', period='10y'):
#     """Fetch EKHOA from Yahoo Finance and convert to TradingView-like format."""
#     print("Fetching missing EKHOA from Yahoo Finance...")
#     df = yf.download('EKHOA.CA', period=period)
#     if df is None or df.empty:
#         print("No data returned from Yahoo Finance for EKHOA.")
#         return False

#     df.reset_index(inplace=True)
#     df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
#     df.rename(columns={
#         'Date': 'date',
#         'Open': 'open',
#         'High': 'high',
#         'Low': 'low',
#         'Close': 'close',
#         'Volume': 'volume'
#     }, inplace=True)

#     df['symbol'] = 'EGX:EKHOA'
#     if 'date' in df.columns:
#         df['date'] = pd.to_datetime(df['date']).dt.date

#     cols_to_keep = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']
#     existing_cols = [c for c in cols_to_keep if c in df.columns]
#     df = df[existing_cols]

#     df.to_csv(output_filename, index=False)
#     print("EKHOA fetched and saved successfully.")
#     return True


def collect_and_combine(output_file=MARKET_DIR / 'raw' / "EGX30_Full_Dataset_Ready.csv"):
    """Read all *_TV_Data.csv files, normalize and combine them into one dataset."""
    print("Collecting and normalizing individual files... ")
    all_files = glob.glob(str(MARKET_DIR / 'raw' / "*_TV_Data.csv"))
    df_list = []
    companies_added = 0

    for file in all_files:
        try:
            df = pd.read_csv(file)
            
            # Extract ticker accurately from filename instead of full string path
            ticker = Path(file).name.split('_')[0]

            # Normalize header variations safely
            if 'Unnamed: 0' in df.columns:
                df.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
            if 'datetime' in df.columns:
                df.rename(columns={'datetime': 'date'}, inplace=True)
            elif 'Date' in df.columns:
                df.rename(columns={'Date': 'date'}, inplace=True)

            df['Ticker'] = ticker
            df_list.append(df)
            companies_added += 1

        except Exception as e:
            print(f"Error reading file {file}: {e}")

    if not df_list:
        print("No files found to combine.")
        return None

    combined_df = pd.concat(df_list, ignore_index=True)
    
    if 'date' in combined_df.columns:
        combined_df['date'] = pd.to_datetime(combined_df['date'], errors='coerce')
        combined_df.sort_values(by=['date', 'Ticker'], inplace=True)

    combined_df.to_csv(output_file, index=False)
    print("-" * 30)
    print("Combined dataset saved successfully!")
    print(f"Total companies processed: {companies_added}")
    print(f"Total rows in dataset: {len(combined_df)}")
    return output_file


def find_missing_in_combined(combined_file=MARKET_DIR / 'raw' / "EGX30_Full_Dataset_Ready.csv"):
    try:
        df = pd.read_csv(combined_file)
    except Exception as e:
        print(f"Could not read combined file {combined_file}: {e}")
        return []

    found_tickers = df['Ticker'].unique().tolist() if 'Ticker' in df.columns else []
    missing = [t for t in EGX30_TICKERS if t not in found_tickers]
    print(f"Missing tickers after pipeline verification: {missing}")
    return missing


# def fetch_missing_from_yahoo_map(mapping, period='10y'):
#     """Fetch tickers from Yahoo using a mapping of TV ticker -> Yahoo ticker."""
#     for tv_ticker, yf_ticker in mapping.items():
#         print(f"Fetching missing {tv_ticker} from Yahoo Finance...")
#         df = yf.download(yf_ticker, period=period)
#         if df is None or df.empty:
#             print(f"No data returned for {tv_ticker} ({yf_ticker}).")
#             continue

#         df.reset_index(inplace=True)
#         df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
#         df.rename(columns={
#             'Date': 'date',
#             'Open': 'open',
#             'High': 'high',
#             'Low': 'low',
#             'Close': 'close',
#             'Volume': 'volume'
#         }, inplace=True)

#         df['symbol'] = f'EGX:{tv_ticker}'
#         if 'date' in df.columns:
#             df['date'] = pd.to_datetime(df['date']).dt.date
            
#         cols_to_keep = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']
#         existing_cols = [col for col in cols_to_keep if col in df.columns]
#         df = df[existing_cols]
#         df.to_csv(MARKET_DIR / 'raw' / f"{tv_ticker}_TV_Data.csv", index=False)
#         print(f"{tv_ticker} data fallback completed.")


def main():
    # Initialize the client session once
    tv = TvDatafeed()

    # Step 1: Broad collection run
    fetch_tv_data(tv, 5000, 'ml')

    # Step 2: Target flaky tickers with robust reconnect logic
    retry_list = ['ESRS', 'MTIE', 'EXPA', 'EGAL']
    fetch_with_retries(tv, retry_list, n_bars=5000, retries=3)

    # Step 3: Specific data source fallback for tracking EKHOA
    #fetch_ekhoa_from_yahoo()

    # Step 4: Run normalizer and combine files
    combined_file = collect_and_combine()

    # Step 5: Check file health metrics and apply secondary Yahoo fallbacks if needed
    # if combined_file:
    #     missing = find_missing_in_combined(combined_file)
        
    #     yahoo_mapping = {'COMI': 'COMI.CA', 'ESRS': 'ESRS.CA'}
    #     active_fallbacks = {k: v for k, v in yahoo_mapping.items() if k in missing}
        
        # if active_fallbacks:
        #     fetch_missing_from_yahoo_map(active_fallbacks)
        #     # Re-combine if fallbacks were needed to update the final dataset
        #     collect_and_combine()


if __name__ == '__main__':
    main()