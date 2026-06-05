from functools import wraps
from api.models import *
import api.common.errors.errors as Errors
from api.common.extentions.extentions import bcrypt, jwt
from flask_jwt_extended import create_access_token, create_refresh_token

def get_user_id_with_uuid(uuid):
    uuid = convert_uuid_str_to_UUID(uuid)
    user = User.query.filter_by(uuid=uuid).first()
    if user:
        return user.user_id
    else:
        raise Errors.UserNotFound
    
def convert_uuid_str_to_UUID(uuid):
    return PyUUID(uuid) if isinstance(uuid, str) else uuid

def required_fields_exist(required_fields, payload):
    missing = [field for field in required_fields if field not in payload]
    if missing:
        raise Errors.InvalidInput
    else:
        return True

def verify_password(hash, password):
    if bcrypt.check_password_hash(hash, password):
        return True
    else:
        raise Errors.IncorrectCredentials