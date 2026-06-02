from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import and_, or_
from api.models import *
from api.app import db
import api.common.errors.errors as Errors
from api.common.errors.app_errors import AppErrors

# Auth
def create_user():
    pass

def get_user_by_email(email):
    pass

def edit_user_settings():
    pass

def delete_user(email):
    pass