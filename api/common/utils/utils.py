from functools import wraps
from flask import request
import me.errors as Errors

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            raise Errors.Unauthorized
        pass

def get_id_from_token(headers):
    pass