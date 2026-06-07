from api.models import *
from api.app import db
import api.common.errors.errors as Errors
from api.common.errors.app_errors import AppErrors
from api.common.extentions.extentions import bcrypt

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
    
def verify_patch_keys(payload):
    if not payload:
        return None
    if 'modifications' not in payload:
        raise Errors.ValidationFailed
    modifications = payload['modifications']
    if isinstance(modifications, list) and len(modifications) == 0:
        return None
    else:
        return modifications
    
def apply_db_updates(record, ALLOWED_UPDATES, modifications):
        is_updated = False
        try:
            for mod in modifications:
                field = mod.get('field')
                new_value = mod.get('value')
                if field in ALLOWED_UPDATES:
                    db_column = ALLOWED_UPDATES[field]
                    setattr(record, db_column, new_value)
                    is_updated = True
            if is_updated:
                db.session.commit()
        except (AppErrors, Exception) as e:
            db.session.rollback()
            if isinstance(e, AppErrors):
                raise e
            else:
                raise Errors.DatabaseError