from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import joblib
import json
import numpy as np
import pandas as pd
import os
import glob
from pathlib import Path
import sys

ROOT_DIR = Path().resolve()
sys.path.append(str(ROOT_DIR))

from config.paths import MARKET_DIR
from config.paths import XGB_MODEL, XGB_MODEL_META
import preprocessing.market_processing.fetch_market_data as Extract
from preprocessing.market_processing.data_cleaning import MarketDataCleaner
from api.app import create_app, db
from api.models import StockPrice, Prediction, RecommendationSet, Recommendation
from api.market.repositories import *
from tvDatafeed import TvDatafeed, Interval

app = create_app()
tv = TvDatafeed()
latest_date = get_latest_date
combined_file_path = MARKET_DIR / 'daily' / "EGX30_Full_Dataset_Ready.csv"

def daily_market_update():
    print('Starting daily market update...')
    Extract.fetch_tv_data(tv, 1, 'daily')
    Extract.fetch_with_retries(tv, 1, 'daily')

    daily_data = Extract.collect_and_combine('daily', combined_file_path)
    Extract.find_missing_in_combined(combined_file_path)

    if daily_data and os.path.exists(daily_data):
        print('Deleting individual raw files...')
        raw_files = glob.glob(str(MARKET_DIR / 'daily' / '*_TV_Data.csv'))
        for file in raw_files:
            try:
                os.remove(file)
            except Exception as e:
                print(f'Could not delete {file}: {e}')
    
    stock_prices_df = pd.read_csv(daily_data)

    try:
        stock_map = {s.ticker_symbol: s.stock_id for s in Stock.query.all()}
        price_list = []

        for _, row in stock_prices_df.iterrows():
            ticker_symbol = row.get('symbol', row.get('ticker'))
            if ':' in str(ticker_symbol):
                ticker_symbol = str(ticker_symbol).split(':')[-1]
            
            date_obj = datetime.strptime(row['date'], '%Y-%m-%d').date()
            price = StockPrice(
                stock_id = stock_map[row['symbol']],
                date = date_obj,
                open_price = row['open'],
                high_price = row['high'],
                low_price = row['low'],
                close_price = row['close'],
                volume = row['volume']
            )
            price_list.append(price)

            if len(price_list) >= 1000:
                db.session.add_all(price_list)
                price_list = []
        if price_list:        
            db.session.add_all(price_list) 
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"Database sync failed: {e}")
    return daily_data

def daily_predictions(daily_data):
    print('Starting daily predictions...')

    if not daily_data or not os.path.exists(daily_data):
        raise FileNotFoundError

    try:
        #load model and meta
        model = joblib.load(XGB_MODEL)
        with open(XGB_MODEL_META, "r") as f:
            meta = json.load(f)

        features = meta["features"]
        medians  = pd.Series(meta["medians"])

        df = pd.read_csv(daily_data)

        X = df[features].copy()
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(medians)
        X = X.values.astype(np.float32)

        raw_preds = model.predict(X)
    
        db.session.add_all(raw_preds) #check
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print('ML pipeline or DB commit failed: {e}')
        raise e
    
    finally:
        if daily_data and os.path.exists(daily_data):
            try:
                os.remove(daily_data)
                print('Deleted market data csv for today.')
            except Exception as e:
                print('Market data csv was not deleted.')

    return print(f'Today\'s predictions: {raw_preds}')

def daily_recommendation_sets(latest_date):
    print('Creating recommendation sets...')

    risk_categories = ['Conservative', 'Moderate', 'Aggressive']
    for category in risk_categories:
        stmt = (
            db.select(RecommendationSet).where(
                RecommendationSet.risk_category == category,
                RecommendationSet.date == latest_date
            )
        )
        existing_set = db.session.execute(stmt).scalar()
        if existing_set:
            print(f"RecommendationSet for {category} on {latest_date} already exists. Skipping creation.")
            continue
        rec_set = RecommendationSet(
            risk_category = category
        )
        db.session.add(rec_set)
        db.session.flush()
    try:
        db.session.commit()
        print(f"Successfully created daily recommendation sets for {latest_date}.")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating recommendation sets: {e}")

def daily_recommendations(latest_date):
    print('Choosing stocks to recommend...')
    predicted_returns = get_all_predicted_returns(latest_date)
    stocks = db.session.execute(db.select(Stock)).scalars().all()
    recommendation_sets = get_latest_recommendation_sets()
    risk_map = {
        'Conservative': 'Low',
        'Moderate': 'Medium',
        'Aggressive': 'High'
    }
    # stock_map = {stock.ticker_symbol: stock for stock in stocks}
    # for set in recommendation_sets:
    #     recommended_stocks = []
    #     for ticker, stock_obj in stock_map.items():
    #         pred_return = predicted_returns.get(ticker)

def daily_pipeline():
    with app.app_context():
        try:
            daily_data = daily_market_update()
            daily_predictions(daily_data)
            daily_recommendation_sets(latest_date)
            daily_recommendations(latest_date)
        except Exception as e:
            print('Error: {e}')

def schedule():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=daily_pipeline, trigger='cron', hour=1, minute=0)
    scheduler.start()