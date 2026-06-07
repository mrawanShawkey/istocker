import api.user.repositories as Repos
from api.common.utils.utils import *

def get_profile(uuid):
    user_id = get_user_id_with_uuid(uuid)
    first_name, last_name, member_since, last_updated = Repos.get_user_personal_info(user_id)
    risk_category, risk_category_ar, description, description_ar, category_score_range = Repos.get_risk_category(user_id)
    risk_capacity = Repos.get_risk_capacity(user_id)
    risk_tolerance = Repos.get_risk_tolerance(user_id)
    total_risk = Repos.get_total_risk(user_id)
    user_responses = Repos.get_user_registration_responses(user_id)
    data = {
        'firstName': first_name,
        'lastName': last_name,
        'memberSince': member_since,
        'lastUpdated': last_updated,
        'riskCategory': risk_category,
        'riskCategoryAr': risk_category_ar,
        'description': description,
        'descriptionAr': description_ar,
        'categoryScoreRange': category_score_range,
        'riskCapacityScore': risk_capacity,
        'riskToleranceScore': risk_tolerance,
        'totalRiskScore': total_risk,
        'userResponses': user_responses,
    }
    return data

def get_settings(uuid):
    user_id = get_user_id_with_uuid(uuid)
    first_name, last_name, member_since, last_updated = Repos.get_user_personal_info(user_id)
    lang, notifs = Repos.get_user_preferences(user_id)
    data = {
        'firstName': first_name,
        'lastName': last_name,
        'memberSince': member_since,
        'lastUpdated': last_updated,
        'lang': lang,
        'notifications': notifs
    }
    return data

def edit_profile(uuid, modifications):
    user_id = get_user_id_with_uuid(uuid)
    Repos.edit_profile(user_id, modifications)

def edit_preferences(uuid, modifications):
    user_id = get_user_id_with_uuid(uuid)
    Repos.edit_preferences(user_id, modifications)