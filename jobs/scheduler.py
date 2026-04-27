from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import joblib
import json
import numpy as np
import pandas as pd 

from config.paths import XGB_MODEL, XGB_MODEL_META

import preprocessing.market_processing.fetch_market_data as Extract
from preprocessing.market_processing.data_cleaning import MarketDataCleaner
from api.app import db
from api.models import StockPrice

today = datetime.now().date()

def daily_market_update(day):
    print('Starting daily market update...')
    raw_data = Extract.fetch_tv_data(n_bars=1)
    if not raw_data:
        return print('Error during fetching')
    processed_data = MarketDataCleaner(raw_data)
    db.session.add_all(processed_data)
    db.session.commit()
    return print(f'Today\'s ({today}) market data: {processed_data}')
    
def daily_predictions():
    daily_market_update(today)
    print('Starting daily predictions...')
    today_data = StockPrice.query.filter_by(date=today).all()
    if not today_data:
        return print("No data for today")
    predictions = []

    #load model and meta
    model = joblib.load(XGB_MODEL)
    with open(XGB_MODEL_META, "r") as f:
        meta = json.load(f)

    features = meta["features"]
    medians  = pd.Series(meta["medians"])

    #convert db to pandas rows 
    rows = [{
        col: getattr(row, col)
        for col in features + ["symbol"]
        if hasattr(row, col)
    } for row in today_data]

    df = pd.DataFrame(rows)

    X = df[features].copy()
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(medians)
    X = X.values.astype(np.float32)

    raw_preds = model.predict(X)

    # TODO: store predictions in db

    db.session.add_all(predictions)
    db.session.commit()
    return print(f'Today\'s predictions: {predictions}')

def schedule():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=daily_predictions, trigger='cron', hour=1, minute=0)
    scheduler.start()