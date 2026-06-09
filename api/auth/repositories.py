from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import and_, or_
from api.models import *
from api.app import db
import api.common.errors.errors as Errors
from api.common.errors.app_errors import AppErrors
from api.common.utils.utils import *
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
    if not user:
        raise Errors.UserNotFound
    return user.uuid, user.password_hash

def email_match_uuid(uuid, email):
    stmt = (
        db.select(User.email, User.password_hash)
        .where(User.uuid==uuid)
    )
    row = db.session.execute(stmt).first()
    if row and row.email == email:
        return row.password_hash
    else:
        raise Errors.IncorrectCredentials

def change_email(uuid, new_email):
    stmt = (
        db.select(User)
        .where(User.uuid==uuid)
    )
    user = db.session.execute(stmt).scalar()
    user.email = new_email
    db.session.commit()

def password_match_uuid(uuid, password):
    stmt = (
        db.select(User.password_hash)
        .where(User.uuid==uuid)
    )
    password_hash = db.session.execute(stmt).scalar()
    verify_password(password_hash, password)

def change_password(uuid, new_password):
    stmt = (
        db.select(User)
        .where(User.uuid==uuid)
    )
    user = db.session.execute(stmt).scalar()
    user.password_hash = bcrypt.generate_password_hash(new_password)
    db.session.commit()
    
def invalidate_token(uuid, token_payloads):
    jtis = [payload['jti'] for payload in token_payloads]
    stmt = db.select(BlockedToken.jti).where(BlockedToken.jti.in_(jtis))
    existing_jtis = set(db.session.scalars(stmt).all())
    block_list = []
    for payload in token_payloads:
        jti = payload['jti']
        if jti in existing_jtis:
            continue
        expiry = datetime.fromtimestamp(payload['exp'], timezone.utc)
        blocked_token = BlockedToken(
            jti = jti,
            uuid = uuid,
            expires_at = expiry
        )
        block_list.append(blocked_token)
    db.session.add_all(block_list)
    db.session.commit()

def is_token_revoked(jti):
    stmt = (
        db.select(BlockedToken.jti)
        .where(BlockedToken.jti==jti)
    )
    token = db.session.execute(stmt).scalar()
    return token is not None

def delete_user(uuid):
    stmt = (
        db.select(User)
        .where(User.uuid==uuid)
    )
    user = db.session.execute(stmt).scalar()
    if not user:
        raise Errors.UserNotFound
    db.session.delete(user)
    db.session.commit()