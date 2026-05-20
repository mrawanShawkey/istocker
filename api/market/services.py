import api.repositories as Repos

def get_market_data():
    top_movers = Repos.get_top_movers()
    top_sectors = Repos.get_top_sectors()
    data = {
        "topMovers": top_movers,
        "topSectors": top_sectors,
    }
    return data

def get_ticker_data(ticker):
    stock_info = Repos.get_stock_info(ticker)
    stock_id = stock_info['stockId']
    stock_name = stock_info['stockName']
    stock_name_ar = stock_info['stockNameAr']
    stock_description = stock_info['stockDescription']
    stock_description_ar = stock_info['stockDescriptionAr']
    sector = stock_info['sector']
    sector_ar = stock_info['sectorAr']
    current_price = Repos.get_current_price(ticker)
    price_difference = Repos.get_price_difference(ticker)
    month_prices = Repos.get_month_prices(ticker)
    data = {
        "stockId": stock_id,
        "stockName": stock_name,
        "stockNameAr": stock_name_ar,
        "stockDescription": stock_description,
        "stockDescriptionAr": stock_description_ar,
        "stockDescription": stock_description,
        "sector": sector,
        "sectorAr": sector_ar,
        "currentPrice": current_price,
        "priceDifference": price_difference,
        "monthPrices": month_prices
    }
    return data