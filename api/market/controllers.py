from flask import Blueprint, request, jsonify
import market.services as Services

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
def get_market_by_ticker(ticker):
    data = Services.get_market_data_by_ticker(ticker)
    response = {
        "success": True,
        "data": data,
        "message": "Stock description and prices returned."
    }
    return jsonify(response), 200