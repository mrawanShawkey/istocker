from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

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
    print('Starting deily predictions...')
    today_data = StockPrice.query.filter_by(date=today).all()
    predictions = []
    # call model when ready, pass today_data, store in predictions
    db.session.add_all(predictions)
    db.session.commit()
    return print(f'Today\'s predictions: {predictions}')

def schedule():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=daily_predictions, trigger='cron', hour=1, minute=0)
    scheduler.start()