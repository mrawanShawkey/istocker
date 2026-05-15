from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt
import auth.services as Services
import auth.utils as Utils
auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    payload = request.get_json()
    response = Services.register(payload)
    return jsonify(response), 201

@auth.route('/login', methods=['POST'])
def login():
    payload = request.get_json()
    response = Services.login(payload)
    return jsonify(response), 200

@auth.route('/refresh', methods=['POST'])
def refresh():
    payload = request.get_json()
    response = Services.refresh(payload)
    return jsonify(response), 200

@auth.route('/change-email', methods=['PATCH'])
def change_email():
    user_access_token = Utils.get_user_token(request.headers)
    payload = request.get_json()
    response = Services.change_email(payload)
    return jsonify(response), 200

@auth.route('/change-password', methods=['PATCH'])
def change_password():
    user_access_token = Utils.get_user_token(request.headers)
    payload = request.get_json()
    response = Services.change_password(payload)
    return jsonify(response), 200

@auth.route('/forgot-password', methods = ['POST'])
def forgot_password():
    payload = request.get_json()
    response = Services.forgot_password(payload)
    return jsonify(response), 200

@auth.route('/reset-password', methods = ['POST'])
def reset_password():
    payload = request.get_json()
    response = Services.reset_password(payload)
    return jsonify(response), 200

@auth.route('/logout', methods=['POST'])
def logout():
    user_access_token = Utils.get_user_token(request.headers)
    payload = request.get_json()
    response = Services.logout(payload)
    return jsonify(response), 200

@auth.route('/delete-account', methods=['DELETE'])
def delete_account():
    user_access_token = Utils.get_user_token(request.headers)
    response = Services.delete_account()
    return jsonify(response), 204