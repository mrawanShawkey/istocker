from flask import Blueprint, request, jsonify
import me.services as Services
from api.common.utils import token_required
import api.common.utils as Utils
import me.utils as Me_Utils
import me.errors as Errors

me = Blueprint('me', __name__)

@me.route('/')
@token_required
def get_me():
    user_id = Utils.get_id_from_token(request.headers)
    data = Services.get_me(user_id)
    response = {
        "success": True,
        "data": data,
        "message": "User data returned."
    }
    return jsonify(response), 200

@me.route('/profile', methods=['PATCH'])
@token_required
def edit_profile():
    payload = request.get_json()
    data = Services.edit_profile(payload)
    response = {
        "success": True,
        "data": data,
        "message": "User data has been changed in the database."
    }
    return jsonify(response), 200

@me.route('/preferences', methods=['PATCH'])
@token_required
def edit_preferences():
    payload = request.get_json()
    data = Services.edit_preferences(payload)
    response = {
        "success": True,
        "data": data,
        "message": "User preference has been changed in the database."
    }
    return jsonify(response), 200

@me.route('/results')
@token_required
def get_results():
    data = Services.get_results()
    response = {
        "success": True,
        "data": data,
        "message": "User risk profile and top 3 recommended stocks returned."
    }
    return jsonify(response), 200