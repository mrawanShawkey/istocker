from datetime import datetime, timedelta
from api.models import *
from app import db

# Auth
def create_user():
    pass

def get_user_by_email(email):
    pass

def edit_user_settings():
    pass

def delete_user(email):
    pass



# Market
def get_current_price(ticker): #float
    stmt = (
    db.select(StockPrice.close_price)
    .join(Stock, StockPrice.stock_id == Stock.stock_id)
    .where(Stock.ticker_symbol == ticker)
    .order_by(StockPrice.date.desc())
    .limit(1)
    )
    price = db.session.execute(stmt).scalar()
    return price or 0.0

def get_price_difference(ticker): #float
    stmt = (
        db.select(StockPrice.close_price)
        .join(Stock, StockPrice.stock_id == Stock.stock_id)
        .where(Stock.ticker_symbol == ticker)
        .order_by(StockPrice.date.desc())
        .limit(2)
    )
    prices = db.session.execute(stmt).scalars.all()
    if len(prices) == 2:
        last_price = prices[0]
        second_to_last = prices[1]
        return last_price - second_to_last
    return 0.0
    

def get_month_prices(ticker): #dict
    stmt = (
        db.select(StockPrice.date, StockPrice.close_price)
        .join(Stock, StockPrice.stock_id == Stock.stock_id)
        .where(Stock.ticker_symbol == ticker)
        .order_by(StockPrice.data.desc())
        .limit(30)
    )
    rows = db.session.execute(stmt).all()
    prices = {row.date.isoformat(): row.close_price for row in rows}
    return prices

def get_stock_info(ticker): #dict
    stmt = (
        db.select(Stock.stock_id, Stock.ticker_symbol, Stock.company_name, Stock.company_name_ar, Sector.sector_name, Sector.sector_name_ar, Stock.description, Stock.description_ar)
        .join(Sector, Stock.sector_id == Sector.sector_id)
        .where(Stock.ticker_symbol == ticker)
    )
    stock_info = db.session.execute(stmt)
    row = stock_info.first()
    if row:
        return {
            "stockId": row.stock_id,
            "ticker": row.ticker_symbol,
            "stockName": row.company_name,
            "stockNameAr": row.company_name_ar,
            "sector": row.sector_name,
            "sectorAr": row.sector_name_ar,
            "description": row.description,
            "descriptionAr": row.description_ar
        }
    return None

def get_top_movers(): #list of dicts
    stmt = (
        db.select(Stock.ticker_symbol, Stock.stock_name, Stock.stock_name_ar)
        .join(StockPrice, Stock.stock_id == StockPrice.stock_id)
        .where()
        .limit(5)
    )
    rows = db.session.execute(stmt).all()
    top_movers = []
    for mover in rows:
        pass


def get_top_sectors(): #list of dicts
    pass



# Me



# Questions