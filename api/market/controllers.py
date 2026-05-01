from flask import request
import market.services as Services

def get_market_data():
    return Services.get_market_data()

def get_market_by_ticker(ticker):
    return Services.get_market_data_by_ticker()