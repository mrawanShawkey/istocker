from collections import defaultdict
from sqlalchemy import and_, or_
from api.models import *
from api.app import db
import api.common.errors.errors as Errors
from api.common.errors.app_errors import AppErrors
from api.common.utils.utils import *

def get_user_risk_category(user_id):
    stmt = (
        db.select(RiskCategory.category_name)
        .join(RiskAssessment, RiskCategory.category_id==RiskAssessment.risk_category_id)
        .where(RiskAssessment.user_id==user_id)
    )
    risk_category = db.session.scalar(stmt)
    return risk_category if risk_category is not None else None

def get_recommended_stocks_ids_with_ranks(risk_category):
    stmt = (
        db.select(
            Recommendation.stock_id,
            Recommendation.rank,
            Recommendation.predicted_return
        )
        .join(RecommendationSet, Recommendation.recommendation_set_id==RecommendationSet.set_id)
        .where(RecommendationSet.risk_category==risk_category)
        .order_by(RecommendationSet.created_at.desc())
        .limit(3)
    )
    rows = db.session.execute(stmt).all()
    return [{'stock_id': row.stock_id, 'predicted_return': row.predicted_return, 'rank': row.rank} for row in rows]

def get_recommendations(risk_category):
    stocks_ids = get_recommended_stocks_ids_with_ranks(risk_category)
    recommendations = []
    for item in stocks_ids:
        stock_id = item.get('stock_id')
        predicted_return = item.get('predicted_return')
        rank = item.get('rank')
        stmt = (
            db.select(Stock).where(Stock.stock_id==stock_id)
        )
        row = db.session.execute(stmt).scalars().first()
        recommendation = {
            'stockId': stock_id,
            'ticker': row.ticker_symbol,
            'companyName': row.company_name,
            'companyNameAr': row.company_name_ar,
            'description': row.description,
            'descriptionAr': row.description_ar,
            'riskLevel': row.risk_level,
            'riskLevelAr': row.risk_level_ar,
            'predictedReturn': predicted_return,
            'rank': rank
        }
        recommendations.append(recommendation)
    return recommendations