from flask import Blueprint, request, jsonify
import market.services as Services

market = Blueprint('market', __name__)

@market.route('/')
def get_market_data():
    payload = request.get_json()
    response = Services.get_market_data(payload)
    return jsonify(response), 200

@market.route('/<string:ticker>')
def get_market_by_ticker(ticker):
    response = Services.get_market_data_by_ticker(ticker)
    return jsonify(response), 200