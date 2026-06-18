"""Daily market-data scheduler.

This module wires APScheduler to a daily pipeline that:
1. downloads one day of EGX market data from TradingView,
2. combines the raw CSV files into one daily CSV,
3. syncs that data into the Flask/SQLAlchemy database,
4. runs the production XGBoost model, and
5. prepares recommendation data.

The module creates a Flask app and TradingView client at import time. The
scheduled job itself must run inside ``app.app_context()`` so Flask-SQLAlchemy
can access configuration and the active database session.
"""

# ``datetime`` parses CSV date strings into Python ``date`` objects before
# inserting rows into the ``stock_prices`` table.
from datetime import datetime

# APScheduler runs Python callables in the background of this process. This is
# not Celery: jobs run only while the Python process that called ``schedule()``
# is alive.
from apscheduler.schedulers.background import BackgroundScheduler

# ``joblib`` loads the trained XGBoost production model from disk.
import joblib

# ``json`` loads the model metadata file that stores feature names and medians.
import json

# NumPy is used to replace infinities and cast model features to float32.
import numpy as np

# Pandas reads/writes the daily market CSV and prepares model input matrices.
import pandas as pd

# ``os`` checks whether generated CSV files exist and removes them after use.
import os

# ``glob`` finds the per-ticker raw CSV files that should be cleaned up.
import glob

# ``Path`` builds project-root-relative paths in a cross-platform way.
from pathlib import Path

# ``sys`` is used to add the project root to ``sys.path`` so this module can be
# executed directly with ``python -m api.jobs.scheduler`` or imported from app
# code without losing access to top-level packages like ``config``.
import sys

ROOT_DIR = Path().resolve()
sys.path.append(str(ROOT_DIR))

# Project paths for market-data output and the production XGBoost artifacts.
from config.paths import MARKET_DIR
from config.paths import XGB_MODEL, XGB_MODEL_META

# The extraction module owns the TradingView fetch, retry, combine, and missing
# ticker checks used by the daily market update.
import preprocessing.market_processing.fetch_market_data as Extract

# Imported for future/expected cleaning work, but not currently used in this
# file. Leaving it in place avoids changing import behavior.
from preprocessing.market_processing.data_cleaning import MarketDataCleaner

# ``create_app`` builds the Flask app; ``db`` is the shared Flask-SQLAlchemy
# extension used for all database reads/writes in the scheduled job.
from api.app import create_app, db

# ORM models touched by the scheduler. Some are currently used only by planned
# recommendation/prediction code, so unused-looking imports may still document
# intended dependencies.
from api.models import StockPrice, Prediction, RecommendationSet, Recommendation

# Repository helpers provide market queries such as ``get_latest_date`` and
# ``get_all_predicted_returns``. The wildcard import also makes ``Stock``
# available here because repositories imports all API models.
from api.market.repositories import *

# TradingView client used to fetch EGX daily candles. ``Interval`` is imported
# for compatibility with TradingView fetch logic, but this file delegates the
# actual interval choice to ``Extract``.
from tvDatafeed import TvDatafeed, Interval

# Import-time setup: this module creates one Flask app and one TradingView
# client. ``daily_pipeline`` later pushes an app context before database work.
app = create_app()
tv = TvDatafeed()

# This stores the function object, not the latest date value. The current code
# passes it into recommendation functions as-is; see docs for the risk.
latest_date = get_latest_date

# Combined daily CSV produced after individual per-ticker files are fetched.
combined_file_path = MARKET_DIR / 'daily' / "EGX30_Full_Dataset_Ready.csv"
risk_categories = ['Conservative', 'Moderate', 'Aggressive']

def daily_market_update():
    """Fetch the latest daily market data and sync it into the database.

    Inputs/parameters:
        None. The function uses the module-level TradingView client, configured
        market-data directory, and Flask-SQLAlchemy session.

    Returns:
        Path-like value returned by ``Extract.collect_and_combine``. This should
        point to the combined daily CSV, or may be ``None`` if no files were
        available to combine.

    Side effects:
        Calls TradingView through ``tvDatafeed``; creates and deletes CSV files
        under ``data/market_data/daily``; inserts ``StockPrice`` rows; commits
        or rolls back the database session; prints progress to stdout.

    Possible errors:
        Network/API errors from TradingView are mostly handled inside
        ``Extract``. CSV read errors, missing columns, missing stock mappings,
        SQLAlchemy errors, or file-system errors can occur. Database sync
        errors are caught and rolled back here, but the combined CSV path is
        still returned.
    """
    print('Starting daily market update...')

    # 1. Fetch one daily candle per EGX30 ticker. The retry pass covers the
    # tickers known to fail more often in the extraction module.
    Extract.fetch_tv_data(tv, 1, 'daily')
    Extract.fetch_with_retries(tv, 1, 'daily')

    # 2. Merge all per-ticker files into the single CSV consumed by both the DB
    # sync and the prediction step. The missing check only reports missing
    # tickers; it does not stop the pipeline.
    daily_data = Extract.collect_and_combine('daily', combined_file_path)
    Extract.find_missing_in_combined(combined_file_path)

    # 3. Once the combined file exists, remove the individual raw files so the
    # next daily run does not reuse stale per-ticker CSVs.
    if daily_data and os.path.exists(daily_data):
        print('Deleting individual raw files...')
        raw_files = glob.glob(str(MARKET_DIR / 'daily' / '*_TV_Data.csv'))
        for file in raw_files:
            try:
                os.remove(file)
            except Exception as e:
                print(f'Could not delete {file}: {e}')
    
    # 4. Load the combined CSV. This requires ``daily_data`` to be a real path;
    # if collection returned ``None``, this line will raise.
    stock_prices_df = pd.read_csv(daily_data)

    try:
        # Map ticker symbols to database primary keys so CSV rows can become
        # ``StockPrice`` ORM objects.
        stock_map = {s.ticker_symbol: s.stock_id for s in Stock.query.all()}
        price_list = []

        for _, row in stock_prices_df.iterrows():
            # TradingView symbols may be saved as ``EGX:COMI``. The local stock
            # table usually stores only ``COMI``, so the prefix is stripped for
            # lookups. Note: the current insert still uses ``row['symbol']``.
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

            # Batch inserts protect memory if the CSV grows beyond a single day.
            if len(price_list) >= 1000:
                db.session.add_all(price_list)
                price_list = []
        if price_list:        
            db.session.add_all(price_list) 
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f'Database sync failed: {e}')
        
    return daily_data

def daily_predictions(daily_data):
    """Run the production model against the combined daily market CSV.

    Args:
        daily_data: Path to the combined daily CSV created by
            ``daily_market_update``.

    Returns:
        Whatever ``print`` returns, currently ``None``. The printed message
        contains the raw model predictions.

    Side effects:
        Loads model artifacts from disk; reads the daily CSV; attempts to write
        predictions to the database; commits or rolls back the database session;
        deletes the combined daily CSV in ``finally``.

    Possible errors:
        Raises ``FileNotFoundError`` when ``daily_data`` is missing. Model load
        errors, missing metadata keys, missing feature columns, model inference
        errors, or SQLAlchemy errors are rolled back and re-raised.
    """
    print('Starting daily predictions...')

    if not daily_data or not os.path.exists(daily_data):
        raise FileNotFoundError

    try:
        # 1. Load the trained model and the companion metadata. The metadata
        # tells the scheduler which dataframe columns to pass to the model and
        # what median values to use for missing numeric features.
        model = joblib.load(XGB_MODEL)
        with open(XGB_MODEL_META, "r") as f:
            meta = json.load(f)

        features = meta['features']
        medians  = pd.Series(meta['medians'])

        df = pd.read_csv(daily_data)
        stock_map = {s.ticker_symbol: s.stock_id for s in Stock.query.all()}

        # 2. Build the exact feature matrix expected by the model: select the
        # configured features, convert infinities to missing values, fill
        # missing values with training medians, then cast to float32.
        X = df[features].copy()
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(medians)
        X = X.values.astype(np.float32)

        # 3. Run inference. ``raw_preds`` is usually a NumPy array, not ORM
        # ``Prediction`` objects; see docs for why the DB insert may fail.
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
        # 4. Delete the combined CSV even if prediction or DB write fails, so
        # the next scheduler run starts from a fresh fetch.
        if daily_data and os.path.exists(daily_data):
            try:
                os.remove(daily_data)
                print('Deleted market data csv for today.')
            except Exception as e:
                print('Market data csv was not deleted.')

    return print(f'Today\'s predictions: {raw_preds}')

def daily_recommendation_sets(latest_date):
    """Create one recommendation set for each supported risk category.

    Args:
        latest_date: Intended to be the market date used for this daily
            recommendation batch.

    Returns:
        None.

    Side effects:
        Inserts up to three ``RecommendationSet`` rows and commits the database
        session. Rolls back on commit errors. Prints progress to stdout.

    Possible errors:
        SQLAlchemy query/flush/commit errors can occur. In the current model,
        ``RecommendationSet`` has ``created_at`` but no ``date`` column, so the
        duplicate-check query may fail before the commit block.
    """
    print('Creating recommendation sets...')

    risk_categories = ['Conservative', 'Moderate', 'Aggressive']
    for category in risk_categories:
        # The intent is idempotency: avoid creating duplicate sets for the same
        # risk category/date. The model currently uses ``created_at`` instead of
        # ``date``, which is documented as a risk.
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
    """Prepare daily stock recommendations from predicted returns.

    Args:
        latest_date: Intended market date for filtering predictions.

    Returns:
        None. The current function is incomplete and does not insert
        ``Recommendation`` rows yet.

    Side effects:
        Reads predictions, stocks, and latest recommendation sets from the
        database. It currently only prepares local variables and prints status.

    Possible errors:
        SQLAlchemy errors can occur while reading from the database. The current
        implementation may also receive a function object instead of a date from
        ``daily_pipeline``.
    """
    print('Choosing stocks to recommend...')

    # These reads are the planned inputs for recommendation selection:
    # predicted returns for the target date, all known stocks, and the latest
    # recommendation-set containers grouped by risk category.
    predicted_returns = get_all_predicted_returns(latest_date)
    stocks = db.session.execute(db.select(Stock)).scalars().all()
    recommendation_sets = get_latest_recommendation_sets()

    # Intended mapping from a user-facing recommendation category to stock risk
    # levels. The selection loop below is still commented out.
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
    """Run the full daily scheduler workflow inside a Flask app context.

    Inputs/parameters:
        None. Uses module-level ``app`` and the helper functions above.

    Returns:
        None.

    Side effects:
        Pushes a Flask application context; fetches external market data;
        reads/writes/deletes CSV files; loads ML artifacts; reads/writes the
        database; prints status/errors.

    Possible errors:
        Any exception from the child steps can occur. The outer ``try`` catches
        exceptions and prints an error message, so APScheduler may treat the job
        as completed even when part of the pipeline failed.
    """
    # Flask-SQLAlchemy needs an app context because this job runs outside a
    # normal HTTP request. Without this, ``db.session`` and model queries can
    # fail with "Working outside of application context".
    with app.app_context():
        try:
            # Startup-to-execution flow:
            # schedule() registers this function with APScheduler.
            # APScheduler wakes up at the cron time and calls daily_pipeline().
            # daily_pipeline() then executes each step in sequence.
            daily_data = daily_market_update()
            daily_email()
            daily_predictions(daily_data)
            daily_recommendation_sets(latest_date)
            daily_recommendations(latest_date)
        except Exception as e:
            print(f'Error: {e}')

def schedule():
    """Create and start the background scheduler for the daily pipeline.

    Inputs/parameters:
        None.

    Returns:
        None. The scheduler instance is local to this function and is not
        returned to the caller.

    Side effects:
        Starts an APScheduler ``BackgroundScheduler`` thread in the current
        process and registers ``daily_pipeline`` as a cron job.

    Trigger logic:
        ``trigger='cron', hour=1, minute=0`` means "run every day when the
        scheduler's timezone reaches 01:00". No timezone is configured here, so
        APScheduler uses its default/local timezone.

    Possible errors:
        APScheduler import/configuration errors, duplicate scheduler starts, or
        process shutdown can stop jobs from running. In multi-worker servers,
        every process that calls this function can start its own scheduler and
        run the job independently.
    """
    scheduler = BackgroundScheduler()
    # Cron trigger: run once per day at 01:00 in the scheduler's configured
    # timezone. Because no job id or persistent job store is configured, this
    # job exists only in memory and can be duplicated if schedule() is called
    # multiple times in the same or multiple processes.
    scheduler.add_job(func=daily_pipeline, trigger='cron', hour=1, minute=0)
    scheduler.start()
