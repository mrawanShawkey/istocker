from datetime import datetime
from apscheduler.schedulers.background import BlockingScheduler
from sqlalchemy import Date
#import joblib
import json
import numpy as np
import pandas as pd
import os
import glob
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
from api.common.utils.utils import get_market_update_html
from api.config import Config
from tvDatafeed import TvDatafeed, Interval

app = create_app()
tv = TvDatafeed()
combined_file_path = MARKET_DIR / 'daily' / "EGX30_Full_Dataset_Ready.csv"
risk_categories = ['Conservative', 'Moderate', 'Aggressive']

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
        
        db.session.add_all(price_list) 
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f'Database sync failed: {e}')
        
    return daily_data

def daily_predictions(daily_data, latest_date):
    print('Starting daily predictions...')

    if not daily_data or not os.path.exists(daily_data):
        raise FileNotFoundError

    try:
        #load model and meta
        model = joblib.load(XGB_MODEL)
        with open(XGB_MODEL_META, "r") as f:
            meta = json.load(f)

        features = meta['features']
        medians  = pd.Series(meta['medians'])

        df = pd.read_csv(daily_data)
        stock_map = {s.ticker_symbol: s.stock_id for s in Stock.query.all()}

        X = df[features].copy()
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(medians)
        X = X.values.astype(np.float32)

        raw_preds = model.predict(X)
    
        predictions = []
        for index, row in df.iterrows():
            symbol = row.get('symbol')
            
            if symbol in stock_map:
                pred_obj = Prediction(
                    stock_id = stock_map[symbol],
                    date = latest_date,
                    predicted_return = float(raw_preds[index]) # Map individual prediction scalar
                )
                predictions.append(pred_obj)

        db.session.add_all(predictions)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f'ML pipeline or DB commit failed: {e}')
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

    try:
        for category in risk_categories:
            stmt = (
                db.select(RecommendationSet).where(
                    RecommendationSet.risk_category == category,
                    db.cast(RecommendationSet.created_at, Date) == latest_date
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
        db.session.commit()
        print(f"Successfully created daily recommendation sets for {latest_date}.")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating recommendation sets: {e}")

def daily_recommendations(latest_date):
    print('Choosing stocks to recommend...')

    recommendation_sets = get_latest_recommendation_sets()

    risk_map = {
        'Conservative': 'Low',
        'Moderate': 'Medium',
        'Aggressive': 'High'
    }

    stmt = (
        db.select(Stock.stock_id, Stock.ticker_symbol, Stock.risk_level, Prediction.predicted_return)
        .join(Prediction, Stock.stock_id==Prediction.stock_id)
        .where(Prediction.date==latest_date)
    )
    stocks = db.sessison.execute(stmt).all()

    for set in recommendation_sets:
        risk_level = risk_map.get(set.risk_category)
        stocks_of_a_category = []
        for stock in stocks:
            if stock.risk_level == risk_level:
                stocks_of_a_category.append(stock)
        stocks_of_a_category.sort(key=lambda x: x.predicted_return, reverse=True)
        top_3_stocks = stocks_of_a_category[:3]

        for rank, stock in enumerate(top_3_stocks, start=1):
            recommendation = Recommendation(
                recommendation_set_id = set.set_id,
                stock_id = stock.stock_id,
                predicted_return = stock.predicted_return,
                rank = rank
            )
            db.session.add(recommendation)
    try:
        db.session.commit()
        print(f'Successfully committed top-3 stock allocations for all risk profiles on {latest_date}.')
    except Exception as e:
        db.session.rollback()
        print(f'Failed to save portfolio recommendations: {e}')

def daily_email():
    stmt = (
        db.select(User.email)
        .join(UserPreference, User.user_id==UserPreference.user_id)
        .where(UserPreference.notifications==1)
    )
    emails = db.session.execute(stmt).scalars().all()

    if not emails:
        print("No users have daily email notifications enabled.")
        return
    try:
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.EMAIL_ADDRESS, Config.EMAIL_PASSWORD)
    except Exception as e:
        print(f"Failed to connect to SMTP Mail Server: {e}")
        return

    subject = 'Daily Market Update.'
    body = get_market_update_html()
    for email in emails:
        try:
            msg = MIMEMultipart()
            msg['From'] = f'<{Config.EMAIL_ADDRESS}>'
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))

            server.sendmail(Config.EMAIL_ADDRESS, email, msg.as_string())

        except Exception as e:
            print(f"Skipping user. Failed to send email to {email}: {e}")
        
    try:
        server.quit()
    except Exception:
        pass

def daily_pipeline():
    with app.app_context():
        try:
            latest_date = get_latest_date()
            daily_data = daily_market_update()
            daily_email()
            daily_predictions(daily_data)
            daily_recommendation_sets(latest_date)
            daily_recommendations(latest_date)
        except Exception as e:
            print(f'Error: {e}')

def schedule():
    scheduler = BlockingScheduler()
    scheduler.add_job(func=daily_pipeline, trigger='cron', hour=1, minute=8)
    scheduler.start()

if __name__ == '__main__':
    schedule()