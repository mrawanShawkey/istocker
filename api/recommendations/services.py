import api.recommendations.repositories as Repos
import api.common.errors.errors as Errors
from api.common.utils.utils import *

def get_recommendations(uuid):
    user_id = get_user_id_with_uuid(uuid)
    risk_category = Repos.get_user_risk_category(user_id)
    if risk_category:
        recommendations = Repos.get_recommendations(risk_category)
        return recommendations
    else:
        return None