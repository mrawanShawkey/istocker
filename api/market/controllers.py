from flask import Blueprint, request, jsonify
import api.market.services as Services
import api.common.errors.errors as Errors

market = Blueprint('market', __name__)

@market.route('/')
def get_market_data():
    data = Services.get_market_data()
    response = {
        "success": True,
        "data": data,
        "message": "Market overview returned."
    }
    return jsonify(response), 200

@market.route('/<string:ticker>')
def get_ticker_data(ticker):
    data = Services.get_ticker_data(ticker)
    response = {
        "success": True,
        "data": data,
        "message": "Stock description and prices returned."
    }
    return jsonify(response), 200