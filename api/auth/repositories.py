from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import and_, or_
from api.models import *
from api.app import db
import api.common.errors.errors as Errors
from api.common.errors.app_errors import AppErrors
from flask_jwt_extended import get_jwt

def does_email_exist(email):
    stmt = (
        db.select(User.email)
        .where(User.email==email)
        .exists()
    )
    return db.session.execute(db.select(stmt)).scalar()

def create_user(first_name, last_name, email, pass_hash):
    user = User(
        first_name = first_name,
        last_name = last_name,
        email = email,
        password_hash = pass_hash
    )
    db.session.add(user)
    db.session.commit()
    return user.uuid

def get_user_by_email(email):
    stmt = (
        db.select(User)
        .where(User.email==email)
    )
    user = db.session.execute(stmt).scalar()
    return user.uuid, user.password_hash

def delete_user(email):
    pass