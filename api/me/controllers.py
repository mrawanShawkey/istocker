from flask import Blueprint, request, jsonify
import me.services as Services

me = Blueprint('me', __name__)

@me.route('/')
def get_me():
    response = Services.get_me()
    return jsonify(response), 200

@me.route('/profile', methods=['PATCH'])
def edit_profile():
    payload = request.get_json()
    response = Services.edit_profile(payload)
    return jsonify(response), 200


@me.route('/preferences', methods=['PATCH'])
def edit_preferences():
    payload = request.get_json()
    response = Services.edit_preferences(payload)
    return jsonify(response), 200

@me.route('/results')
def get_results():
    response = Services.get_results()
    return jsonify(response), 200