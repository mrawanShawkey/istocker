from api.common.extentions.extentions import db
from datetime import date as date_type, datetime, timezone, timedelta
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, BigInteger, Float, Numeric, Boolean, Text, DateTime, Date, JSON, ForeignKey, Enum
from typing import Optional, List

# Enum Classes
class RiskCat(PyEnum):
    CONSERVATIVE = 'Conservative'
    MODERATE = 'Moderate'
    AGGRESSIVE = 'Aggressive'

class RiskCatAr(PyEnum):
    CONSERVATIVE = 'محافظ'
    MODERATE = 'متوسط'
    AGGRESSIVE = 'جريء'

class RiskLevel(PyEnum):
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'

class RiskLevelAr(PyEnum):
    LOW = 'منخفض'
    MEDIUM = 'متوسط'
    HIGH = 'مرتفع'

class QuestionType(PyEnum):
    REGISTRATION = 'Registration'
    QUESTIONNAIRE = 'Questionnaire'

# Models
class User(db.Model):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(100), unique=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    tokens: Mapped[List['RefreshToken']] = relationship('RefreshToken', back_populates='user')
    user_profile: Mapped['UserProfile'] = relationship('UserProfile', back_populates='user', uselist=False)
    risk_assessments: Mapped[List['RiskAssessment']] = relationship('RiskAssessment', back_populates='user')
    user_responses: Mapped[List['UserResponse']] = relationship('UserResponse', back_populates='user')

    def __repr__(self):
        return f'<User: {self.username}>'
    
class RefreshToken(db.Model):
    __tablename__ = 'refresh_tokens'

    token_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.user_id'))
    token: Mapped[str] = mapped_column(Text, index=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(days=7))

    user: Mapped['User'] = relationship('User', back_populates='tokens')

    def __repr__(self):
        return f'<Refresh token value for user {self.user}. Expires at: {self.expires_at}>'

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    profile_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.user_id'), unique=True)
    risk_capacity_score: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user_responses: Mapped[List['UserResponse']] = relationship('UserResponse', back_populates='user_profile')
    user: Mapped['User'] = relationship('User', back_populates='user_profile')

    def __repr__(self):
        return f'<UserProfile {self.profile_id} for user {self.user_id}.>'

class RiskCategory(db.Model):
    __tablename__ = 'risk_categories'

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_name: Mapped[RiskCat] = mapped_column(Enum(RiskCat, values_callable=lambda x: [e.value for e in x]), unique=True)
    category_name_ar: Mapped[RiskCatAr] = mapped_column(Enum(RiskCatAr, values_callable=lambda x: [e.value for e in x]), unique=True)
    description: Mapped[str] = mapped_column(Text, unique=True)
    description_ar: Mapped[str] = mapped_column(Text, unique=True)
    min_score: Mapped[int] = mapped_column(Integer, unique=True)
    max_score: Mapped[int] = mapped_column(Integer, unique=True)

    risk_assessments: Mapped[List['RiskAssessment']] = relationship('RiskAssessment', back_populates='risk_category')

    def __repr__(self):
        return f'<Risk Category: {self.category_name}. {self.description}.>'

class RiskAssessment(db.Model):
    __tablename__ = 'risk_assessments'

    assessment_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.user_id'))
    risk_tolerance_score: Mapped[int | None] = mapped_column(Integer)
    total_risk_score: Mapped[int | None] = mapped_column(Integer)
    risk_category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('risk_categories.category_id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user_responses: Mapped[List['UserResponse']] = relationship('UserResponse', back_populates='risk_assessment')
    user: Mapped['User'] = relationship('User', back_populates='risk_assessments')
    risk_category: Mapped[Optional['RiskCategory']] = relationship('RiskCategory', back_populates='risk_assessments')

    def __repr__(self):
        return f'<RiskAssessment {self.assessment_id} for user {self.user_id} with total risk score {self.total_risk_score}. Taken at {self.created_at}.>'

class Question(db.Model):
    __tablename__ = 'questions'

    question_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_number: Mapped[int] = mapped_column(Integer)
    question_text: Mapped[str] = mapped_column(Text, unique=True)
    question_text_ar: Mapped[str] = mapped_column(Text, unique=True)
    question_type: Mapped[QuestionType] = mapped_column(Enum(QuestionType, values_callable=lambda x: [e.value for e in x]))

    options: Mapped[List['Option']] = relationship('Option', back_populates='question')
    user_responses: Mapped[List['UserResponse']] = relationship('UserResponse', back_populates='question')

    def __repr__(self):
        return f'<Question {self.question_id}: {self.question_text}.>'

class Option(db.Model):
    __tablename__ = 'options'

    option_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey('questions.question_id'))
    option_number: Mapped[int] = mapped_column(Integer)
    option_text: Mapped[str] = mapped_column(Text)
    option_text_ar: Mapped[str] = mapped_column(Text)
    weight: Mapped[float] = mapped_column(Float)

    user_responses: Mapped[List['UserResponse']] = relationship('UserResponse', back_populates='option')
    question: Mapped['Question'] = relationship('Question', back_populates='options')

    def __repr__(self):
        return f'<Option {self.option_id}: {self.option_text} (weight: {self.weight}).>'

class UserResponse(db.Model):
    __tablename__ = 'user_responses'
    
    response_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.user_id'))
    assessment_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('risk_assessments.assessment_id'))
    profile_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('user_profiles.profile_id'))
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey('questions.question_id'))
    option_id: Mapped[int] = mapped_column(Integer, ForeignKey('options.option_id'))
    
    user: Mapped['User'] = relationship('User', back_populates='user_responses')
    risk_assessment: Mapped[Optional['RiskAssessment']] = relationship('RiskAssessment', back_populates='user_responses')
    user_profile: Mapped[Optional['UserProfile']] = relationship('UserProfile', back_populates='user_responses')
    question: Mapped['Question'] = relationship('Question', back_populates='user_responses')
    option: Mapped['Option'] = relationship('Option', back_populates='user_responses')

    def __repr__(self):
        return f'<UserResponse {self.response_id}: for question {self.question_id}, user {self.user_id} chose option {self.option_id} in assessment {self.assessment_id}.>'
    
class Sector(db.Model):
    __tablename__ = 'sectors'

    sector_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sector_name: Mapped[str] = mapped_column(String(100), unique=True)
    sector_name_ar: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text)
    description_ar: Mapped[str] = mapped_column(Text)

    stocks: Mapped[List['Stock']] = relationship('Stock', back_populates='sector')

    def __repr__(self):
        return f'<{self.sector_name} sector. Description: {self.description}>'

class Stock(db.Model):
    __tablename__ = 'stocks'

    stock_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker_symbol: Mapped[str] = mapped_column(String(10), unique=True)
    company_name: Mapped[str] = mapped_column(String(255))
    company_name_ar: Mapped[str] = mapped_column(String(255))
    sector_id: Mapped[int] = mapped_column(Integer, ForeignKey('sectors.sector_id'))
    description: Mapped[str] = mapped_column(Text)
    description_ar: Mapped[str] = mapped_column(Text)
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel, values_callable=lambda x: [e.value for e in x]))
    risk_level_ar: Mapped[RiskLevelAr] = mapped_column(Enum(RiskLevelAr, values_callable=lambda x: [e.value for e in x]))

    stock_prices: Mapped[List['StockPrice']] = relationship('StockPrice', back_populates='stock')
    predictions: Mapped[List['Prediction']] = relationship('Prediction', back_populates='stock')
    recommendations: Mapped[List['Recommendation']] = relationship('Recommendation', back_populates='stock')
    sector: Mapped['Sector'] = relationship('Sector', back_populates='stocks')

    def __repr__(self):
        return f'<Stock {self.ticker_symbol}: {self.company_name}>'

class StockPrice(db.Model):
    __tablename__ = 'stock_prices'

    price_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_id: Mapped[int] = mapped_column(Integer, ForeignKey('stocks.stock_id'))
    date: Mapped[date_type] = mapped_column(Date)
    open_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    high_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    low_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    close_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    volume: Mapped[int] = mapped_column(BigInteger)

    stock: Mapped['Stock'] = relationship('Stock', back_populates='stock_prices')

    def __repr__(self):
        return f'<StockPrice {self.price_id} for stock {self.stock_id} on {self.date} closed at {self.close_price}>'
    
class Prediction(db.Model):
    # Model output, not user specific. Stores predicted one year return for every stock. Refreshed daily.
    __tablename__ = 'predictions'

    prediction_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_id: Mapped[int] = mapped_column(Integer, ForeignKey('stocks.stock_id'))
    date: Mapped[date_type] = mapped_column(Date)
    predicted_return: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    stock: Mapped['Stock'] = relationship('Stock', back_populates='predictions')

    def __repr__(self):
        return f'<Prediction for stock {self.stock_id}: {self.predicted_return} on {self.date}>'
    
class RecommendationSet(db.Model):
    # The "bag". One row per risk category per daily refresh. Just groups recommendations together cleanly.
    __tablename__ = 'recommendation_sets'

    set_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    risk_category: Mapped[RiskCat] = mapped_column(Enum(RiskCat, values_callable=lambda x: [e.value for e in x]))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    recommendations: Mapped[List['Recommendation']] = relationship('Recommendation', back_populates='recommendation_set')

    def __repr__(self):
        return f'<RecommendationSet {self.set_id} for level {self.risk_category} on {self.created_at}>'
    
class Recommendation(db.Model):
    #  The actual three stocks. Each row is one stock, points back to its RecommendationSet. Three rows per set.
    __tablename__ = 'recommendations'

    recommendation_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recommendation_set_id: Mapped[int] = mapped_column(Integer, ForeignKey('recommendation_sets.set_id'))
    stock_id: Mapped[int] = mapped_column(Integer, ForeignKey('stocks.stock_id'))
    predicted_return: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    rank: Mapped[int] = mapped_column(Integer)

    recommendation_set: Mapped['RecommendationSet'] = relationship('RecommendationSet', back_populates='recommendations')
    stock: Mapped['Stock'] = relationship('Stock', back_populates='recommendations')

    def __repr__(self):
        return f'<Recommendation rank {self.rank} in set {self.recommendation_set_id}: stock {self.stock_id}>'