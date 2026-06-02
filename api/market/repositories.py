from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import and_, or_
from api.models import *
from api.app import db
import api.common.errors.errors as Errors
from api.common.errors.app_errors import AppErrors

def get_latest_date():
    stmt = (
        db.select(StockPrice.date)
        .order_by(StockPrice.date.desc())
        .limit(1)
    )
    return db.session.execute(stmt).scalar()

# def get_previous_date():
#     stmt = (
#         db.select(StockPrice.date)
#         .order_by(StockPrice.date.desc())
#         .limit(1)
#     )
#     return db.session.execute(stmt).scalar()
    
def get_all_tickers():
    return db.session.execute(db.select(Stock.ticker_symbol)).scalars().all()

def ticker_exists(ticker):
    stmt = (
        db.select(Stock.ticker_symbol)
        .where(Stock.ticker_symbol == ticker)
    )
    ticker = db.session.execute(stmt).scalar_one_or_none()
    if not ticker:
        raise Errors.TickerNotFound
    return True

def get_all_current_prices(latest_date): #float
    stmt = (
        db.select(Stock.ticker_symbol, StockPrice.close_price)
        .outerjoin(
            StockPrice,
            and_(
                Stock.stock_id == StockPrice.stock_id,
                StockPrice.date == latest_date
            )
        )
    )
    rows = db.session.execute(stmt).all()
    return {row.ticker_symbol: row.close_price for row in rows}

# def get_all_percent_differences(latest_date, previous_date): #float
#     stmt = (
#         db.select(Stock.ticker_symbol, StockPrice.close_price, StockPrice.date)
#         .outerjoin(
#             StockPrice,
#             and_ (
#                 StockPrice.stock_id == Stock.stock_id,
#                 or_(
#                     StockPrice.date == latest_date,
#                     StockPrice.date == previous_date
#                 )
#             )
#         )
#         .order_by(StockPrice.date.desc())
#     )
#     rows = db.session.execute(stmt).all()
#     for row in rows:
#     if len(prices) == 2:
#         last_price = prices[0]
#         second_to_last_price = prices[1]
#         percent_change = ((last_price - second_to_last_price) / second_to_last_price) * 100
#         return round(percent_change, 2)
#     return None

def get_predicted_return(ticker):
    stmt = (
    db.select(Stock.ticker_symbol, Prediction.predicted_return)
    .join(Prediction, Stock.stock_id == Prediction.stock_id)
    .where(Stock.ticker_symbol == ticker)
    .order_by(Prediction.date.desc())
    .limit(1)
    )
    predicted_return = db.session.execute(stmt).scalar()
    return predicted_return

def get_all_predicted_returns(latest_date):
    stmt = (
        db.select(Stock.ticker_symbol, Prediction.predicted_return)
        .outerjoin(
            Prediction,
            and_(
                Stock.stock_id == Prediction.stock_id,
                Prediction.date == latest_date
            )
        )
    )
    rows = db.session.execute(stmt).scalar()
    return {row.ticker_symbol: row.predicted_return for row in rows}
    
def get_month_prices(ticker): #list of dicts
    stmt = (
        db.select(StockPrice.date, StockPrice.close_price)
        .join(Stock, StockPrice.stock_id == Stock.stock_id)
        .where(Stock.ticker_symbol == ticker)
        .order_by(StockPrice.date.desc())
        .limit(30)
    )
    rows = db.session.execute(stmt).all()
    prices = [
        {
            "date": row.date.isoformat(),
            "price": row.close_price
        }
        for row in rows
    ]
    return prices

def get_stock_info(ticker): #dict
    if ticker_exists(ticker):
        stmt = (
            db.select(Stock.stock_id, Stock.company_name, Stock.company_name_ar, Sector.sector_name, Sector.sector_name_ar, Stock.description, Stock.description_ar)
            .join(Sector, Stock.sector_id == Sector.sector_id)
            .where(Stock.ticker_symbol == ticker)
        )
        row = db.session.execute(stmt).first()
        if row:
            return {
                "stockId": row.stock_id,
                "companyName": row.company_name,
                "companyNameAr": row.company_name_ar,
                "description": row.description,
                "descriptionAr": row.description_ar,
                "sector": row.sector_name,
                "sectorAr": row.sector_name_ar,
            }
        raise Errors.MarketDataUnavailable

# def get_top_movers(): #list of dicts
#     price_differences = get_all_percent_differences()
#     stmt = (
#         db.select(Stock.stock_id, Stock.ticker_symbol, Stock.company_name, Stock.company_name_ar)
#     )
#     rows = db.session.execute(stmt).all()
#     all_movers = [
#         {
#             "stockId": row.stock_id,
#             "ticker": row.ticker_symbol,
#             "companyName": row.company_name,
#             "companyNameAr": row.company_name_ar,
#             "priceDifference": price_differences.get(row.ticker_symbol, 0.0)
#         }
#         for row in rows
#     ]
#     top_movers = sorted(
#         all_movers,
#         key = lambda x: x["priceDifference"],
#         reverse = True,
#     )[:5]
#     for mover in top_movers:
#         del mover["priceDifference"]
#     return top_movers

# def get_top_sectors(): #list of dicts
#     price_differences = get_all_percent_differences()
#     stmt = (
#         db.select(Stock.ticker_symbol, Stock.sector_id, Sector.sector_name, Sector.sector_name_ar)
#         .join(Sector, Stock.sector_id == Sector.sector_id)
#     )
#     pass