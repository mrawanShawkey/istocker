from pathlib import Path
import sys

ROOT_DIR = Path().resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from api.models import User, UserProfile, RiskCategory, RiskAssessment, Question, Option, UserResponse 
from api.models import Sector, Stock, StockPrice, Prediction, RecommendationSet, Recommendation, MarketIndex, IndexPrice
from flask import render_template, request, url_for, redirect

def register_routes(app, db):
    #routes go here
    pass