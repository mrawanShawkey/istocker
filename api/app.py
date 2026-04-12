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
    app.secret_key = 'SOME KEYYYY'

    login_manager = LoginManager()
    login_manager.init_app(app)

    #LOGIN FUNCTIONALITY
    from models import User
    @login_manager.user_loader
    def load_user(user_name, password):
        pass

    bcrypt = Bcrypt(app)

    db.init_app(app)

    from api.routes import register_routes
    register_routes(app, db, bcrypt)

    migrate = Migrate(app, db)

    from seed import seed
    app.cli.command('seed')(seed)

    return app
