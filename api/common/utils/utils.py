from functools import wraps
from flask import request
from api.models import *
import api.common.errors.errors as Errors
from api.common.extentions.extentions import bcrypt, jwt
from flask_jwt_extended import create_access_token, create_refresh_token


def get_user_id_with_uuid(uuid):
    user = User.query.filter_by(uuid=uuid).first()
    if user:
        return user.user_id
    else:
        raise Errors.UserNotFound

## Password Hashing
def hash_password(password):
    return bcrypt.generate_password_hash(password)

## Verify Password (bcrypt.compare)!!!!!!!!!!!!!!!!!!!!!
def verify_password(email, password):
    # check email
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