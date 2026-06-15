import heapq
from collections import defaultdict
from sqlalchemy import and_, or_
from api.models import *
from api.app import db
import api.common.errors.errors as Errors
from api.common.errors.app_errors import AppErrors

def get_latest_date():
    stmt = (
        db.select(StockPrice.date)
        .distinct()
        .order_by(StockPrice.date.desc())
        .limit(1)
    )
    return db.session.execute(stmt).scalar()

def get_previous_date():
    stmt = (
        db.select(StockPrice.date)
        .distinct()
        .order_by(StockPrice.date.desc())
        .offset(1)
        .limit(1)
    )
    return db.session.execute(stmt).scalar()
    
def get_all_tickers():
    return db.session.execute(db.select(Stock.ticker_symbol)).scalars().all()

def ticker_exists(ticker):
    stmt = (
        db.select(Stock.ticker_symbol)
        .where(Stock.ticker_symbol==ticker)
    )
    ticker = db.session.execute(stmt).scalar_one_or_none()
    if not ticker:
        raise Errors.TickerNotFound
    return True

# /market
def get_all_current_prices(latest_date):
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

def get_all_percent_differences(latest_date, previous_date):
    stmt = (
        db.select(Stock.ticker_symbol, StockPrice.close_price, StockPrice.date)
        .outerjoin(
            StockPrice,
            and_ (
                StockPrice.stock_id == Stock.stock_id,
                or_(
                    StockPrice.date == latest_date,
                    StockPrice.date == previous_date
                )
            )
        )
        .order_by(Stock.ticker_symbol, StockPrice.date.desc())
    )
    rows = db.session.execute(stmt).all()
    ticker_prices = defaultdict(list)
    for row in rows:
        ticker_prices[row.ticker_symbol].append(row.close_price)
    percent_differences = {}
    for ticker, prices in ticker_prices.items():
        if len(prices) == 2 and None not in prices:
            last_price = prices[0]
            second_to_last_price = prices[1]
            if second_to_last_price > 0:
                percent_change = ((last_price - second_to_last_price) / second_to_last_price) * 100
                percent_differences[ticker] = round(percent_change)
            else:
                percent_differences[ticker] = None
        else:
            percent_differences[ticker] = None
    return percent_differences

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
        db.select(Stock.ticker_symbol, Stock.risk_level, Prediction.predicted_return)
        .outerjoin(
            Prediction,
            and_(
                Stock.stock_id == Prediction.stock_id,
                Prediction.date == latest_date
            )
        )
    )
    rows = db.session.execute(stmt).all()
    return {row.ticker_symbol: {'predicted_return': row.predicted_return, 'risk_level': row.risk_level} for row in rows}
    
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

def get_top_movers(previous_date, latest_date):
    percent_differences = get_all_percent_differences(previous_date, latest_date)
    clean_differences = {ticker: difference for ticker, difference in percent_differences.items() if difference is not None}
    top_tickers = heapq.nlargest(5, clean_differences, clean_differences.get)
    stmt = (
        db.select(Stock.stock_id, Stock.ticker_symbol, Stock.company_name, Stock.company_name_ar)
        .where(Stock.ticker_symbol.in_(top_tickers))
    )
    rows = db.session.execute(stmt).all()
    top_movers = {
        row.ticker_symbol: {
            'stockId': row.stock_id,
            'companyName': row.company_name,
            'companyNameAr': row.company_name_ar,
            'percentDifference': percent_differences.get(row.ticker_symbol, 0.0)
        }
        for row in rows
    }
    top_movers_ranked = [top_movers[ticker] for ticker in top_tickers if ticker in top_movers]
    return top_movers_ranked

def get_all_sectors():
    return db.session.execute(db.select(Sector.sector_name)).scalars().all()

def get_top_sectors():
    latest_date = get_latest_date()
    previous_date = get_previous_date()
    stmt = (
        db.select(Sector.sector_id, Sector.sector_name, Sector.sector_name_ar, StockPrice.date, StockPrice.close_price)
        .join(Stock, Sector.sector_id == Stock.sector_id)
        .join(StockPrice, Stock.stock_id == StockPrice.stock_id)
        .where(StockPrice.date.in_([latest_date, previous_date]))
        .order_by(Stock.ticker_symbol, StockPrice.date.desc())
    )
    rows = db.session.execute(stmt).all()
    sector_maps = {}
    for row in rows:
        if row.sector_name not in sector_maps:
            sector_maps[row.sector_name] = {
                'sector_id': row.sector_id,
                'latest': 0.0, 
                'previous': 0.0, 
                'name_ar': row.sector_name_ar
            }
        price_as_float = float(row.close_price) if row.close_price is not None else 0.0
        if row.date == latest_date:
            sector_maps[row.sector_name]['latest'] += price_as_float
        elif row.date == previous_date:
            sector_maps[row.sector_name]['previous'] += price_as_float
    calculated_sectors = []
    for name, data in sector_maps.items():
        prev = data['previous']
        lat = data['latest']
        if prev == 0:
            continue 
        percent_change = ((lat - prev) / prev) * 100
        calculated_sectors.append({
            'sectorId': data['sector_id'],
            'sectorName': name,
            'sectorNameAr': data['name_ar'],
            'percentDifference': round(percent_change, 2),
        })
    top_5_sectors = sorted(
        calculated_sectors, 
        key=lambda x: x['percentDifference'], 
        reverse=True
    )[:5]
    return top_5_sectors

# /market<ticker>
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
                'stockId': row.stock_id,
                'companyName': row.company_name,
                'companyNameAr': row.company_name_ar,
                'description': row.description,
                'descriptionAr': row.description_ar,
                'sector': row.sector_name,
                'sectorAr': row.sector_name_ar,
            }
        raise Errors.MarketDataUnavailable
    
#scheduler
def get_latest_recommendation_sets():
    latest_date = get_latest_date() #covert to date only instead of datetime
    stmt = (
        db.select(RecommendationSet)
        .where(RecommendationSet.created_at==latest_date)
    )
    sets = db.session.execute(stmt).all()
    return sets