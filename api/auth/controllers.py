from flask import request
from flask_jwt_extended import get_jwt
import auth.services as Services
import auth.utils as Utils

def register():
    data = request.get_json()
    return Services.register(data['firstName'], data['lastName'], data['email'], data['password'])

def login():
    data = request.get_json()
    return Services.login(data['email'], data['password'])

def refresh():
    data = request.get_json()
    return Services.refresh(data['refreshToken'])

def change_email():
    user_access_token = Utils.get_user_token(request.headers) #implement
    data = request.get_json()
    return Services.change_email(data['oldEmail'], data['password'], data['newEmail'])

def change_password():
    user_access_token = Utils.get_user_token(request.headers)
    data = request.get_json()
    return Services.change_password(data['oldPassword'], data['newPassword'])

def logout():
    user_access_token = Utils.get_user_token(request.headers)
    data = request.get_json()
    return Services.logout()

def delete_account():
    user_access_token = Utils.get_user_token(request.headers)
    return Services.delete_account()