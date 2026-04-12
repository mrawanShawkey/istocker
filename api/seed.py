from pathlib import Path
import sys

ROOT_DIR = Path().resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from api.app import create_app, db
from api.models import RiskLevel, QuestionType
from api.models import RiskCategory, Question, Option, Sector, Stock, StockPrice, MarketIndex, IndexPrice
from config.paths import CLEANED_MARKET_FILE, OPTIONS, QUESTIONS, SECTORS, STOCKS
import pandas as pd

def seed():

    #RiskCategory
    categories = [
        RiskCategory(category_name=RiskLevel.CONSERVATIVE, description='You are a Conservative investor. You prioritize capital preservation above all else, and prefer stable, well-established companies with predictable returns. You tend to accept lower yields in exchange for reduced risk and are most comfortable holding positions in blue-chip stocks with strong fundamentals and a consistent dividend history.', min_score=0, max_score=33),
        RiskCategory(category_name=RiskLevel.MODERATE, description='You are a Moderate investor. You seek a balance between growth and stability, and are comfortable accepting some market fluctuation in pursuit of reasonable returns. You tend to diversify across sectors and prefer companies with solid financials and a credible growth story — neither the most defensive nor the most speculative names on the market.', min_score=34, max_score=66),
        RiskCategory(category_name=RiskLevel.AGGRESSIVE, description='You are an Aggressive investor. You prioritize high growth potential and are willing to tolerate significant short-term volatility to achieve above-average returns. You tend to gravitate toward high-momentum stocks, emerging opportunities, and companies with disruptive potential — understanding that higher reward comes with higher risk.', min_score=67, max_score=100)
    ]
    db.session.add_all(categories)
    db.session.commit()
    print('Risk categories seeded.')


    #Question
    questions_df = pd.read_csv(QUESTIONS)
    for _, row in questions_df.iterrows():
        question = Question(
            question_number = row['question_number'],
            question_text = row['question_text'],
            question_type = QuestionType(row['question_type'])
        )
        db.session.add(question)
    db.session.commit()
    print('Questions seeded.')


    #Option
    options_df = pd.read_csv(OPTIONS)
    for _, row in options_df.iterrows():
        option = Option(
            question_id = row['question_id'],
            option_number = row['option_number'],
            option_text = row['option_text'],
            weight = row['weight']
        )
        db.session.add(option)
    db.session.commit()
    print('Options seeded.')


    #Sector
    sectors_df = pd.read_csv(SECTORS)
    for _, row in sectors_df.iterrows():
        sector = Sector(
            sector_name = row['sector_name'],
            description = row['description']
        )
        db.session.add(sector)
    db.session.commit()
    print('Sectors seeded')


    #Stock
    stocks_df = pd.read_csv(STOCKS)
    for _, row in stocks_df.iterrows():
        stock = Stock(
            ticker_symbol = row['ticker_symbol'],
            company_name = row['company_name'],
            sector_id = row['sector_id'],
            description = row['description'],
            risk_level = row['risk_level']
        )
        db.session.add(stock)
    db.session.commit()
    print('Stocks seeded.')


    #StockPrice
    stock_prices_df = pd.read_csv(CLEANED_MARKET_FILE)
    stock_map = {s.ticker_symbol: s.id for s in Stock.query.all()}
    for _, row in stock_prices_df.iterrows():
        price = StockPrice(
            stock_id = stock_map[row['ticker_symbol']],
            date = row['date'],
            open_price = row['open'],
            high_price = row['high'],
            low_price = row['low'],
            close_price = row['close'],
            volume = row['volume']
        )
        db.session.add(price)
    db.session.commit()
    print('Stock prices seeded.')


    #MarketIndex
    index = MarketIndex(ticker_symbol='EGX30', index_name='Egyptian Exchange 30', description='Egypt\'s premier benchmark index, tracking the top 30 companies listed on the Egyptian Exchange in terms of liquidity and activity, with broad representation across key economic sectors.')
    db.session.add(index)
    db.session.commit()
    print('Market Indices seeded.')


    #IndexPrice
    index_prices_df = pd.read_csv()
    index_map = {i.ticker_symbol: i.id for i in MarketIndex.query.all()}
    for _, row in index_prices_df.iterrows():
        price = IndexPrice(
            index_id = index_map[row['ticker_symbol']],
            date = row['date'],
            open_price = row['open'],
            high_price = row['high'],
            low_price = row['low'],
            close_price = row['close'],
            volume = row['volume']
        )
        db.session.add(price)
    db.session.commit()
    print('Index prices seeded.')