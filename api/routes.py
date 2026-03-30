from api.models import User, UserProfile, RiskCategory, RiskAssessment, Question, Option, UserResponse 
from api.models import Sector, Stock, StockPrice, Prediction, RecommendationSet, Recommendation, MarketIndex, IndexPrice
from flask import render_template, request, url_for, redirect
from flask_login import login_user, logout_user, current_user, login_required

def register_routes(app, db, bcrypt):
    pass
    