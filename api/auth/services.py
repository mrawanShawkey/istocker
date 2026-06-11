import api.auth.repositories as Repos
import api.common.errors.errors as Errors
from api.common.utils.utils import *
from api.common.extentions.extentions import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token

def register(first_name, last_name, email, password):
    if Repos.does_email_exist(email):
        raise Errors.UserAlreadyExists
    pass_hash = bcrypt.generate_password_hash(password, 10).decode('utf-8')
    uuid = Repos.create_user(first_name, last_name, email, pass_hash)
    access_token = create_access_token(uuid)
    refresh_token = create_refresh_token(uuid)
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

def refresh(uuid):
    data = {'newAccessToken': create_access_token(uuid)}
    return data
    
def change_email(uuid, old_email, password, new_email):
    password_hash = Repos.email_match_uuid(uuid, old_email)
    verify_password(password_hash, password)
    if Repos.does_email_exist(new_email):
        raise Errors.UserAlreadyExists
    Repos.change_email(uuid, new_email)

def change_password(uuid, old_password, new_password, re_password):
    Repos.password_match_uuid(uuid, old_password)
    if new_password != re_password:
        raise Errors.ValidationFailed
    Repos.change_password(uuid, new_password)

# def forgot_password(email):
#     Repos.does_email_exist(email)
#     #send code to email

# def reset_password(code, email, new_password, re_password):
#     #check if code is valid
#     if new_password != re_password:
#         raise Errors.ValidationFailed
#     uuid, hash = Repos.get_user_by_email(email)
#     Repos.change_password(uuid, new_password)

def logout(uuid, access_payload, refresh_payload):
    uuid = convert_uuid_str_to_UUID(uuid)
    token_payloads = [access_payload, refresh_payload]
    Repos.invalidate_token(uuid, token_payloads)

def delete_account(uuid):
    uuid = convert_uuid_str_to_UUID(uuid)
    Repos.delete_user(uuid)