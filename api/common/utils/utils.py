from functools import wraps
from flask import request
import api.common.errors.errors as Errors
from api.common.extentions.extentions import bcrypt, jwt
from flask_jwt_extended import create_access_token, create_refresh_token
import api.repositories as Repo

## Decorator for Required Auth!!!!!!!!!!!!!!!!!!!!!
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            raise Errors.Unauthorized
        pass

## Decode JWT to user_id!!!!!!!!!!!!!!!!!!!!!
def get_id_from_token(headers):
    pass

## Password Hashing
def hash_password(password):
    return bcrypt.generate_password_hash(password)

## Verify Password (bcrypt.compare)!!!!!!!!!!!!!!!!!!!!!
def verify_password(email, password):
    hash = Repo.get_user_by_email(email)
    if bcrypt.check_password_hash(password, hash):
        return True
    else:
        raise Errors.IncorrectCredentials

## Access Token (jwt.sign)!!!!!!!!!!!!!!!!!!!!!
def create_access_token(uuid):
    pass

## Refresh Token (jwt.sign)!!!!!!!!!!!!!!!!!!!!!
def create_refresh_token(uuid):
    pass

##Verify Token (jwt.verify)!!!!!!!!!!!!!!!!!!!!!
def verify_token(token):
    pass