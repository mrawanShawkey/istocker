from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import and_, or_
from api.models import *
from api.app import db
import api.common.errors.errors as Errors
from api.common.errors.app_errors import AppErrors
from api.common.utils.utils import *

def get_user_personal_info(user_id):
    stmt = (
        db.select(User.first_name, User.last_name, User.created_at, User.updated_at)
        .where(User.user_id==user_id)
    )
    user = db.session.execute(stmt).first()
    if not user:
        raise Errors.UserNotFound
    first_name, last_name, member_since, last_updated = user
    return first_name, last_name, member_since, last_updated

def get_user_preferences(user_id):
    stmt = (
        db.select(UserPreference.language, UserPreference.notifications)
        .where(UserPreference.user_id==user_id)
    )
    preference = db.session.execute(stmt).first()
    if not preference:
        raise Errors.UserNotFound
    lang = preference.language.value
    notifs = preference.notifications
    return lang, notifs

def get_risk_category(user_id):
    stmt = (
        db.select(RiskCategory)
        .join(RiskAssessment, RiskCategory.category_id==RiskAssessment.risk_category_id)
        .where(RiskAssessment.user_id==user_id)
    )
    row = db.session.scalars(stmt).first()
    if not row:
        return None, None, None, None, None
    risk_category = row.category_name
    risk_category_ar = row.category_name_ar
    description = row.description
    description_ar = row.description_ar
    min_score = str(row.min_score)
    max_score = str(row.max_score)
    category_score_range = f'({min_score}-{max_score})'
    return risk_category, risk_category_ar, description, description_ar, category_score_range

def get_risk_capacity(user_id):
    stmt = (
        db.select(UserProfile.risk_capacity_score)
        .where(UserProfile.user_id==user_id)
    )
    risk_capacity = db.session.scalars(stmt).first()
    return None if risk_capacity is None else risk_capacity

def get_risk_tolerance(user_id):
    stmt = (
        db.select(RiskAssessment.risk_tolerance_score)
        .where(RiskAssessment.user_id==user_id)
    )
    risk_tolerance = db.session.scalars(stmt).first()
    return None if risk_tolerance is None else risk_tolerance

def get_total_risk(user_id):
    stmt = (
        db.select(RiskAssessment.total_risk_score)
        .where(RiskAssessment.user_id==user_id)
    )
    total_risk = db.session.scalars(stmt).first()
    return None if total_risk is None else total_risk

def get_user_registration_responses(user_id):
    stmt = (
        db.select(Option.option_id)
        .join(UserResponse, Option.option_id==UserResponse.option_id)
        .where(UserResponse.assessment_id==None, UserResponse.user_id==user_id)
    )
    options = db.session.scalars(stmt)
    if not options:
        return None
    else:
        responses = [{'optionId': option_id} for option_id in options]
        return responses
    
def edit_profile(user_id, modifications):
    stmt = (
        db.select(User)
        .where(User.user_id==user_id)
    )
    user = db.session.scalars(stmt).first()
    if not user:
        raise Errors.UserNotFound
    ALLOWED_UPDATES = {
        'firstName': 'first_name',
        'lastName': 'last_name'
    }
    apply_db_updates(user, ALLOWED_UPDATES, modifications)

def edit_preferences(user_id, modifications):
    stmt = (
        db.select(UserPreference)
        .where(UserPreference.user_id==user_id)
    )
    user = db.session.scalars(stmt).first()
    if not user:
        raise Errors.UserNotFound
    ALLOWED_UPDATES = {
        'lang': 'language',
        'notifs': 'notifications'
    }
    apply_db_updates(user, ALLOWED_UPDATES, modifications)