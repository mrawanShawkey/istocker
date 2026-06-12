from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
# import joblib
import json
import numpy as np
import pandas as pd 
from pathlib import Path
import sys

ROOT_DIR = Path().resolve()
sys.path.append(str(ROOT_DIR))
from config.paths import MARKET_DIR

from config.paths import XGB_MODEL, XGB_MODEL_META

import preprocessing.market_processing.fetch_market_data as Extract
from preprocessing.market_processing.data_cleaning import MarketDataCleaner
from api.app import db
from api.models import StockPrice, Prediction, RecommendationSet, Recommendation
from api.market.repositories import *

latest_date = get_latest_date

def daily_market_update():
    print('Starting daily market update...')
    Extract.fetch_tv_data(n_bars=1) #parameter to cahnge dir /raw/training , /raw/daily
    processed_data = MarketDataCleaner() #check what this cleans and returns (new dirs, don't overwrite training dataset)
    db.session.add_all(processed_data) #should take a list of row prices
    db.session.commit()
    return print(f'{latest_date} market data: {processed_data}')
    
def daily_predictions():
    print('Starting daily predictions...')
    stmt = (
        db.stmt(
            db.select(StockPrice)
            .where(StockPrice.date==latest_date)
        )
    )
    latest_prices = db.session.execute(stmt).all()

    predictions = []
    #load model and meta
    # model = joblib.load(XGB_MODEL)
    with open(XGB_MODEL_META, "r") as f:
        meta = json.load(f)

    features = meta["features"]
    medians  = pd.Series(meta["medians"])

    #convert db to pandas rows 
    rows = [{
        col: getattr(row, col)
        for col in features + ["symbol"]
        if hasattr(row, col)
    } for row in latest_prices]

    df = pd.DataFrame(rows)

    X = df[features].copy()
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(medians)
    X = X.values.astype(np.float32)

    # raw_preds = model.predict(X)
    
    db.session.add_all(predictions) #check
    db.session.commit()
    return print(f'Today\'s predictions: {predictions}')

def daily_recommendation_sets():
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

def daily_recommendations():
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

def schedule():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=daily_market_update, trigger='cron', hour=1, minute=0)
    scheduler.add_job(func=daily_predictions, trigger='cron', hour=1, minute=0) #how to make those execute sequentially
    scheduler.add_job(func=daily_recommendation_sets, trigger='cron', hour=1, minute=0)
    scheduler.add_job(func=daily_recommendations, trigger='cron', hour=1, minute=0)
    scheduler.start()