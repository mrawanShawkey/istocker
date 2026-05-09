from flask import request, jsonify
from flask_jwt_extended import get_jwt
import auth.services as Services
import auth.utils as Utils

def register():
    try:
        payload = request.get_json()
        Services.register(payload)
    except:
        pass

def login():
    try:
        payload = request.get_json()
        Services.login(payload)
    except:
        pass

def refresh():
    try:
        payload = request.get_json()
        Services.refresh(payload)
    except: 
        pass

def change_email():
    try:
        user_access_token = Utils.get_user_token(request.headers)
        payload = request.get_json()
        Services.change_email(payload)
    except:
        pass

def change_password():
    try:
        user_access_token = Utils.get_user_token(request.headers)
        payload = request.get_json()
        Services.change_password(payload)
    except:
        pass

def forgot_password():
    try:
        payload = request.get_json()
        Services.forgot_password(payload)
    except:
        pass

def reset_password():
    try:
        payload = request.get_json()
        Services.reset_password(payload)
    except:
        pass

def logout():
    try:
        user_access_token = Utils.get_user_token(request.headers)
        payload = request.get_json()
        Services.logout(payload)
    except:
        pass

def delete_account():
    try:
        user_access_token = Utils.get_user_token(request.headers)
        Services.delete_account()
    except:
        pass