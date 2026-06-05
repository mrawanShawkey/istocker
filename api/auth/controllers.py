from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
import api.auth.services as Services
from api.common.utils.utils import *
import api.common.errors.errors as Errors
auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    payload = request.get_json()
    required_fields = ['firstName', 'lastName', 'email', 'password']
    if required_fields_exist(required_fields, payload):
        first_name = payload.get('firstName')
        last_name = payload.get('lastName')
        email = payload.get('email')
        password = payload.get('password')
        data = Services.register(first_name, last_name, email, password)
        response = {
            'success': True,
            'data': data,
            'message': 'User created successfully.'
        }
        return jsonify(response), 201

@auth.route('/login', methods=['POST'])
def login():
    payload = request.get_json()
    required_fields = ['email', 'password']
    if required_fields_exist(required_fields, payload):
        email = payload.get('email')
        password = payload.get('password')
        data = Services.login(email, password)
        response = {
            'success': True,
            'data': data,
            'message': 'User logged in successfully.'
        }
        return jsonify(response), 200

@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    uuid = get_jwt_identity()
    data = Services.refresh(uuid)
    response = {
        'success': True,
        'data': data,
        'message': 'New access token issued.'
    }
    return jsonify(response), 200

@auth.route('/change-email', methods=['PATCH'])
@jwt_required()
def change_email():
    payload = request.get_json()
    required_fields = ['oldEmail', 'password', 'newEmail']
    if required_fields_exist(required_fields, payload):
        uuid = convert_uuid_str_to_UUID(get_jwt_identity())
        old_email = payload.get('oldEmail')
        password = payload.get('password')
        new_email = payload.get('newEmail')
        Services.change_email(uuid, old_email, password, new_email)
        response = {
            'success': True,
            'data': None,
            'message': 'Email sucessfully changed.'
        }
        return jsonify(response), 200

@auth.route('/change-password', methods=['PATCH'])
@jwt_required()
def change_password():
    payload = request.get_json()
    required_fields = ['oldPassword', 'newPassword', 'rePassword']
    if required_fields_exist(required_fields, payload):
        uuid = convert_uuid_str_to_UUID(get_jwt_identity())
        old_password = payload.get('oldPassword')
        new_password = payload.get('newPassword')
        re_password = payload.get('rePassword')
        Services.change_password(uuid, old_password, new_password, re_password)
        response = {
            'success': True,
            'data': None,
            'message': 'Password changed successfully.'
        }
        return jsonify(response), 200

# @auth.route('/forgot-password', methods = ['POST'])
# def forgot_password():
#     payload = request.get_json()
#     Services.forgot_password(payload)
#     response = {
#         'success': True,
#         'data': None,
#         'message': 'Verification code sent to email.'
#     }
#     return jsonify(response), 200

# @auth.route('/reset-password', methods = ['POST'])
# def reset_password():
#     payload = request.get_json()
#     Services.reset_password(payload)
#     response = {
#         'success': True,
#         'data': None,
#         'message': 'Password changed successfully.'
#     }
#     return jsonify(response), 200

@auth.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    uuid = get_jwt_identity()
    payload = request.get_json()
    Services.logout(uuid, payload)
    response = {
        'success': True,
        'data': None,
        'message': 'User logged out.'
    }
    return jsonify(response), 200

@auth.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    uuid = get_jwt_identity()
    Services.delete_account(uuid)
    response = {
        'success': True,
        'data': None,
        'message': 'User account deleted.'
    }
    return jsonify(response), 200