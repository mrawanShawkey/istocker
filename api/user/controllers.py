from flask import Blueprint, request, jsonify
import api.user.services as Services
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.common.utils.utils import *
import api.common.errors.errors as Errors

user = Blueprint('user', __name__)

@user.route('/profile')
@jwt_required()
def get_profile():
    uuid = get_jwt_identity()
    data = Services.get_profile(uuid)
    response = {
       'success': True,
        'data': data,
        'message': 'User profile returned.'
    }
    return jsonify(response), 200

@user.route('/settings')
@jwt_required()
def get_settings():
    uuid = get_jwt_identity()
    data = Services.get_settings(uuid)
    response = {
        'success': True,
        'data': data,
        'message': 'User settings returned.'
    }
    return jsonify(response), 200

@user.route('/profile', methods=['PATCH'])
@jwt_required()
def edit_profile():
    payload = request.get_json()
    modifications = verify_patch_keys(payload)
    if modifications is None:
        message = 'No updates were made'
    else:
        uuid = get_jwt_identity()
        data = Services.edit_profile(uuid, modifications)
        message = 'User profile has been updated.'
    response = {
        'success': True,
        'data': data,
        'message': message
    }
    return jsonify(response), 200

@user.route('/preferences', methods=['PATCH'])
@jwt_required()
def edit_preferences():
    payload = request.get_json()
    modifications = verify_patch_keys(payload)
    if modifications is None:
        message = 'No updates were made'
    else:
        uuid = get_jwt_identity()
        Services.edit_preferences(uuid, modifications)
        message = 'User preferences have been updated.'
    response = {
        'success': True,
        'data': None,
        'message': message
    }
    return jsonify(response), 200