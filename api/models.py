from app import db
from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime, Date, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'User'
    user_id = db.Column(primary_key=True)
    email = db.Column(db.Text)

class RiskCategory(db.Model):
    __tablename__ = 'RiskCategory'

class Question(db.Model):
    __tablename__ = 'Question'

class UserResponse(db.Model):
    __tablename__ = 'UserResponse'

class Stock(db.Model):
    __tablename__ = 'Stock'

class Sector(db.Model):
    __tablename__ = 'Sector'

class StockPrice(db.Model):
    __tablename__ = 'StockPrice'

class Recommendation(db.Model):
    __tablename__ = 'Recommendation'

class MarketIndex(db.Model):
    __tablename__ = 'MarketIndex'

class IndexPrice(db.Model):
    __tablename__ = 'IndexPrice'

# class Watchlist(db.Model):
#     __tablename__ = 'WatchList'

