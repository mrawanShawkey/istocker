from flask import Flask
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./database.db'

    db.init_app(app)

    from routes import register_routes
    register_routes(app, db)

    migrate = Migrate(app, db)

    return app
