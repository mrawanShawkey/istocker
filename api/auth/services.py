import api.auth.repositories as Repos
import api.common.errors.errors as Errors
from api.common.utils.utils import *
from api.common.extentions.extentions import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token

def register(first_name, last_name, email, password):
    if Repos.does_email_exist(email):
        raise Errors.UserAlreadyExists
    pass_hash = bcrypt.generate_password_hash(password)
    uuid = Repos.create_user(first_name, last_name, email, pass_hash)
    access_token = create_access_token(str(uuid))
    refresh_token = create_refresh_token(str(uuid))
    data = {
        'accessToken': access_token,
        'refreshToken': refresh_token
    }
    return data

def login(email, password):
    if not Repos.does_email_exist(email):
        raise Errors.IncorrectCredentials
    uuid, password_hash = Repos.get_user_by_email(email)
    verify_password(password_hash, password)
    access_token = create_access_token(uuid)
    refresh_token = create_refresh_token(uuid)
    data = {
        'accessToken': access_token,
        'refreshToken': refresh_token
    }
    return data

def refresh(refresh_token):
    pass

def change_email(payload):
    pass

def change_password(old_password, new_password, new_password_re):
    pass

def forgot_password(payload):
    pass

def reset_password(payload):
    pass

def logout(payload):
    pass

def delete_account():
    pass