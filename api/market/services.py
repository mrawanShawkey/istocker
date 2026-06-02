import api.market.repositories as Repos

def get_market_data():
    latest_date = Repos.get_latest_date()
    previous_date = Repos.get_previous_date()
    all_stocks_current_prices = Repos.get_all_current_prices(latest_date)
    all_stocks_percent_differences = Repos.get_all_percent_differences(latest_date, previous_date)
    all_stocks_predicted_returns = Repos.get_all_predicted_returns(latest_date)
    combined_current_prices = [
        {
            "ticker": ticker,
            "currentPrice": price,
            "percentDifference": all_stocks_percent_differences.get(ticker, 0.0),
            "predictedReturn": all_stocks_predicted_returns.get(ticker, 0.0)
        }
        for ticker, price in all_stocks_current_prices.items()
    ]
    top_movers = Repos.get_top_movers()
    top_sectors = Repos.get_top_sectors()
    data = {
        "date": latest_date,
        "currentPrices": combined_current_prices,
        "topMovers": top_movers,
        "topSectors": top_sectors,
    }
    return data

def get_ticker_data(ticker):
    stock_info = Repos.get_stock_info(ticker)
    month_prices = Repos.get_month_prices(ticker)
    data = {
        **stock_info,
        "monthPrices": month_prices
    }
    return data