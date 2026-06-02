from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import and_, or_
from api.models import *
from api.app import db
import api.common.errors.errors as Errors
from api.common.errors.app_errors import AppErrors
from api.common.utils.utils import *

def get_risk_scores(uuid): #dict
    user_id = get_user_id_with_uuid(uuid)
    # get risk_capacity from user profile
    # get risk_tolerance from assessment
    # get total_risk from assessment
    # scores = {risk_capacity, risk_tolerance, total_risk, risk_category}
    # return dict of category and scores