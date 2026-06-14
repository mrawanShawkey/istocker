from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import and_, or_
from api.models import *
from api.app import db
import api.common.errors.errors as Errors
from api.common.errors.app_errors import AppErrors
from api.common.utils.utils import *

def get_question_types():
    stmt = (db.select(Question.question_type).distinct())
    types = db.session.execute(stmt).scalars().all()
    question_types = [q_type.value for q_type in types]
    return question_types

# GET /questions/?type=x
def get_questions_and_options(q_type):
    stmt = (
        db.select(
            Question.question_id,
            Question.question_number,
            Question.question_text,
            Question.question_text_ar,
            Question.question_format,
            Option.option_id,
            Option.option_number,
            Option.option_text,
            Option.option_text_ar
        )
        .join(Option, Question.question_id == Option.question_id)
        .where(Question.question_type == q_type)
        .order_by(Question.question_number.asc(), Option.option_number.asc())
    )
    rows = db.session.execute(stmt).all()
    question_groups = defaultdict(lambda:{
        'questionId': None,
        'questionNumber': None,
        'questionText': None,
        'questionTextAr': None,
        'questionFormat': None,
        'options': []
        })
    for row in rows:
        q_id = row.question_id
        question_groups[q_id]['questionId'] = row.question_id
        question_groups[q_id]['questionNumber'] = row.question_number
        question_groups[q_id]['questionText'] = row.question_text
        question_groups[q_id]['questionTextAr'] = row.question_text_ar
        question_groups[q_id]['questionFormat'] = row.question_format.value
        question_groups[q_id]['options'].append({
            'optionId': row.option_id,
            'optionNumber': row.option_number,
            'optionText': row.option_text,
            'optionTextAr': row.option_text_ar
        })
    questions = list(question_groups.values())
    return questions

# POST /questions/responses/?type=x
def submit_responses(uuid, q_type, responses):
    user_id = get_user_id_with_uuid(uuid)
    if q_type == 'Questionnaire':
        assessment = RiskAssessment(
            user_id = user_id
        )
        db.session.add(assessment)
        db.session.flush()
        assessment_id = assessment.assessment_id
    else:
        assessment_id = None
    try:
        for item in responses:
            q_id = item.get('questionId')
            o_id = item.get('optionId')
            if q_id is None or o_id is None:
                raise Errors.ValidationFailed
            response = UserResponse(
                user_id = user_id,
                assessment_id = assessment_id,
                question_id = q_id,
                option_id = o_id
            )
            db.session.add(response)
        db.session.commit()
    except (AppErrors, Exception) as e:
        db.session.rollback()
        if isinstance(e, AppErrors):
            raise e
        else:
            raise Errors.DatabaseError

def calculate_and_store_risk_score(uuid, q_type, responses):
    user_id = get_user_id_with_uuid(uuid)
    score = 0
    for item in responses:
        option_id = item.get('optionId')
        stmt = (
            db.select(Option.weight)
            .where(Option.option_id==option_id)
        )
        weight = db.session.execute(stmt).scalar()
        score += weight
    if q_type == 'Registration':
        risk_capacity = round((score/4) * 100)
        stmt = (
            db.select(UserProfile)
            .where(UserProfile.user_id==user_id)
        )
        row = db.session.execute(stmt).scalars().first()
        if row:
            row.risk_capacity_score = risk_capacity
            db.session.commit()
        else:
            raise Errors.RecordNotFound
        return risk_capacity
    else:
        risk_tolerance = round((score/17) * 100)
        stmt = (
            db.select(RiskAssessment)
            .where(RiskAssessment.user_id==user_id)
            .order_by(RiskAssessment.created_at.desc())
        )
        row = db.session.execute(stmt).scalars().first()
        if row:
            row.risk_tolerance_score = risk_tolerance
            db.session.commit()
        return risk_tolerance
    
def get_risk_capacity(uuid):
    user_id = get_user_id_with_uuid(uuid)
    stmt = (
        db.select(UserProfile.risk_capacity_score)
        .where(UserProfile.user_id==user_id)
    )
    risk_capacity = db.session.execute(stmt).scalar()
    return risk_capacity

def get_risk_tolerance(user_id):
    stmt = (
        db.select(RiskAssessment.risk_tolerance_score)
        .where(RiskAssessment.user_id==user_id)
    )
    risk_tolerance = db.session.execute(stmt).scalar()
    return risk_tolerance

def calculate_and_store_total_risk(uuid, risk_capacity, risk_tolerance):
    user_id = get_user_id_with_uuid(uuid)
    total_risk = round((0.3 * risk_tolerance + 0.7 * risk_capacity))
    stmt = (
            db.select(RiskAssessment)
            .where(RiskAssessment.user_id==user_id)
            .order_by(RiskAssessment.created_at.desc())
        )
    row = db.session.execute(stmt).scalars().first()
    if row:
        row.total_risk_score = total_risk
        db.session.commit()
    else:
        raise Errors.RecordNotFound
    return total_risk

def get_and_store_risk_category(uuid, total_risk):
    user_id = get_user_id_with_uuid(uuid)
    stmt = (
        db.select(RiskCategory)
        .where(RiskCategory.min_score <= total_risk, RiskCategory.max_score >= total_risk)
    )
    risk_category_row = db.session.scalars(stmt).first()
    min_score = str(risk_category_row.min_score)
    max_score = str(risk_category_row.max_score)
    category_score_range = f'({min_score}-{max_score})'
    stmt = (
            db.select(RiskAssessment)
            .where(RiskAssessment.user_id==user_id)
            .order_by(RiskAssessment.created_at.desc())
        )
    risk_assessment_row = db.session.execute(stmt).scalars().first()
    if risk_assessment_row:
        risk_assessment_row.risk_category_id = risk_category_row.category_id
        db.session.commit()
    else:
        raise Errors.RecordNotFound
    return risk_category_row.category_name.value, risk_category_row.category_name_ar.value, risk_category_row.description, risk_category_row.description_ar, category_score_range

#PATCH /questions/responses
def calculate_risk_capacity(user_id):
    stmt = (
        db.select(Option.weight)
        .join(UserResponse, Option.option_id==UserResponse.option_id)
        .where(UserResponse.user_id==user_id, UserResponse.risk_assessment.is_(None))
    )
    weights = db.session.execute(stmt).scalars().all()
    if not weights:
        return 0
    risk_capacity = round((sum(weights)/4) * 100)
    return risk_capacity

def edit_responses(uuid, modifications):
    user_id = get_user_id_with_uuid(uuid)
    try:
        for item in modifications:
            q_id = item.get('questionId')
            o_id = item.get('optionId')
            if q_id is None or o_id is None:
                raise Errors.ValidationFailed
            stmt = (
                db.select(UserResponse).
                where(UserResponse.user_id == user_id, UserResponse.question_id == q_id)
            )
            response_record = db.session.scalar(stmt)
            if response_record:
                response_record.option_id = o_id
            else:
                raise Errors.RecordNotFound
        db.session.commit()
        updated_risk_capacity = calculate_risk_capacity(user_id)
        risk_tolerance = get_risk_tolerance(user_id)
        updated_total_risk_score = calculate_and_store_total_risk(uuid, updated_risk_capacity, risk_tolerance)
        get_and_store_risk_category(uuid, updated_total_risk_score)
    except (AppErrors, Exception) as e:
        db.session.rollback()
        if isinstance(e, AppErrors):
            raise e
        else:
            raise Errors.DatabaseError