from flask import jsonify
import api.questions.repositories as Repos
import api.common.errors.errors as Errors

def get_question_types():
    return Repos.get_question_types()

def get_questions(q_type):
    if q_type not in get_question_types():
        raise Errors.MissingQuestionType
    data = Repos.get_questions_and_options(q_type)
    return data

def submit_responses(uuid, q_type, responses):
    if q_type not in get_question_types():
        raise Errors.MissingQuestionType
    if q_type == 'Registration':
        if not len(responses) == 4:
            raise Errors.InvalidInput
        Repos.submit_responses(uuid, q_type, responses)
        risk_capacity = Repos.calculate_and_store_risk_score(uuid, q_type, responses)
        return None
    else:
        if not len(responses) == 17:
            raise Errors.InvalidInput
        Repos.submit_responses(uuid, q_type, responses)
        risk_capacity = Repos.get_risk_capacity(uuid)
        risk_tolerance = Repos.calculate_and_store_risk_score(uuid, q_type, responses)
        total_risk = Repos.calculate_and_store_total_risk(uuid, risk_capacity, risk_tolerance)
        risk_category, risk_category_ar, description, description_ar, category_score_range = Repos.get_and_store_risk_category(uuid, total_risk)
        recommendations = Repos.get_recommendations(risk_category)
        data = {
            'riskCategory': risk_category,
            'riskCategoryAr': risk_category_ar,
            'description': description,
            'descriptionAr': description_ar,
            'categoryScoreRange': category_score_range,
            'riskCapacityScore': risk_capacity,
            'riskToleranceScore': risk_tolerance,
            'totalRiskScore': total_risk,
            'recommendations': recommendations
        }
        return data

def edit_responses(uuid, edited_responses):
    Repos.edit_responses(uuid, edited_responses)