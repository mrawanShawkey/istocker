from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)
bcrypt = Bcrypt()
jwt = JWTManager()