from datetime import datetime
from api.app import create_app, db
from api.models import RiskCat, RiskCatAr, RiskLevel, RiskLevelAr, QuestionType
from api.models import RiskCategory, Question, Option, Sector, Stock, StockPrice
from config.paths import CLEAN_MARKET_DATA, SECTORS, STOCKS
import pandas as pd

def seed():
    #RiskCategory
    if RiskCategory.query.first():
        print('Risk categories already seeded.')
    else:
        categories = [
            RiskCategory(
                category_name=RiskCat.CONSERVATIVE, 
                category_name_ar=RiskCatAr.CONSERVATIVE, 
                description='You are a conservative investor. You prioritize capital preservation above all else, and prefer stable, well-established companies with predictable returns. You tend to accept lower yields in exchange for reduced risk and are most comfortable holding positions in blue-chip stocks with strong fundamentals and a consistent dividend history.', 
                description_ar='أنت مستثمر متحفظ. تضع الحفاظ على رأس المال فوق كل اعتبار، وتفضل الشركات المستقرة والراسخة ذات العوائد المتوقعة. تميل إلى قبول عوائد أقل مقابل تقليل المخاطر، وتشعر براحة أكبر في الاحتفاظ بمراكز في الأسهم القيادية ذات الأسس القوية وتاريخ توزيع أرباح ثابت.', 
                min_score=0, 
                max_score=33
            ),
            RiskCategory(
                category_name=RiskCat.MODERATE, 
                category_name_ar=RiskCatAr.MODERATE, 
                description='You are a moderate investor. You seek a balance between growth and stability and are comfortable accepting some market fluctuation in pursuit of reasonable returns. You tend to diversify across sectors and prefer companies with solid financials and a credible growth story.', 
                description_ar='أنت مستثمر معتدل. تسعى لتحقيق التوازن بين النمو والاستقرار، وتتقبل بعض تقلبات السوق في سبيل الحصول على عوائد معقولة. تميل إلى التنويع عبر القطاعات وتفضل الشركات ذات الملاءة المالية القوية وقصة نمو موثوقة.', 
                min_score=34, 
                max_score=66
            ),
            RiskCategory(
                category_name=RiskCat.AGGRESSIVE, 
                category_name_ar=RiskCatAr.AGGRESSIVE, 
                description='You are an aggressive investor. You prioritize high growth potential and are willing to tolerate significant short-term volatility to achieve above-average returns. You tend to gravitate toward high-momentum stocks, emerging opportunities, and companies with disruptive potential, understanding that higher reward comes with higher risk.', 
                description_ar='أنت مستثمر جريء. تعطي الأولوية لإمكانيات النمو العالية ولديك استعداد لتحمل تقلبات قوية قصيرة المدى لتحقيق عوائد أعلى من المتوسط. تميل إلى الانجذاب نحو الأسهم ذات الزخم العالي، والفرص الناشئة، والشركات ذات الإمكانيات الابتكارية، مدركاً أن المكافآت الأعلى تأتي مع مخاطر أعلى.', 
                min_score=67, 
                max_score=100
            )
        ]
        db.session.add_all(categories)
        db.session.commit()
        print('Risk categories seeded.')


    #Question
    if Question.query.first():
       print('Questions already seeded.')
    else:
        questions_df = pd.read_csv(QUESTIONS)
        for _, row in questions_df.iterrows():
            question = Question(
                question_number = row['question_number'],
                question_text = row['question_text'],
                question_text_ar = row['question_text_ar'],
                question_type = QuestionType(row['question_type'])
            )
            db.session.add(question)
        db.session.commit()
        print('Questions seeded.')


    Option
    if Option.query.first():
       print('Options already seeded.')
    else:
        options_df = pd.read_csv(OPTIONS)
        for _, row in options_df.iterrows():
            option = Option(
                question_id = row['question_id'],
                option_number = row['option_number'],
                option_text = row['option_text'],
                option_text_ar = row['option_text_ar'],
                weight = row['weight']
            )
            db.session.add(option)
        db.session.commit()
        print('Options seeded.')


    #Sector
    if Sector.query.first():
        print('Sectors already seeded.') 
    else:
        sectors_df = pd.read_csv(SECTORS)
        for _, row in sectors_df.iterrows():
            sector = Sector(
                sector_name = row['sector_name'],
                sector_name_ar = row['sector_name_ar'],
                description = row['description'],
                description_ar = row['description_ar']
            )
            db.session.add(sector)
        db.session.commit()
        print('Sectors seeded')


    #Stock
    if Stock.query.first():
        print('Stocks already seeded.')
    else:
        stocks_df = pd.read_csv(STOCKS)
        for _, row in stocks_df.iterrows():
            stock = Stock(
                ticker_symbol = row['ticker_symbol'],
                company_name = row['company_name'],
                company_name_ar = row['company_name_ar'],
                sector_id = row['sector_id'],
                description = row['description'],
                description_ar = row['description_ar'],
                risk_level = RiskLevel(row['risk_level']),
                risk_level_ar = RiskLevelAr(row['risk_level_ar'])
            )
            db.session.add(stock)
        db.session.commit()
        print('Stocks seeded.')


    #StockPrice
    if StockPrice.query.first():
        print('Stock prices already seeded.')
    else:
        stock_prices_df = pd.read_csv(CLEAN_MARKET_DATA)
        stock_map = {s.ticker_symbol: s.stock_id for s in Stock.query.all()}
        price_list = []
        for _, row in stock_prices_df.iterrows():
            date_obj = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S').date()
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
        db.session.add_all(price_list) 
        db.session.commit()
        print('Stock prices seeded.')

def clear():
    StockPrice.query.delete()
    Stock.query.delete()
    Sector.query.delete()
    Option.query.delete()
    Question.query.delete()
    RiskCategory.query.delete()
    db.session.commit()
    print('Database cleared.')