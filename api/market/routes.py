from flask import request, Blueprint
import market.controllers as Controllers

market = Blueprint('market', __name__)

@market.route('/')
def get_market_data():
    return Controllers.get_market_data()

@market.route('/<string:ticker>')
def get_market_data_by_ticker(ticker):
    return Controllers.get_market_data_by_ticker(ticker)
