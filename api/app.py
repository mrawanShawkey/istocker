from flask import Flask
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from api.config import Config
from api.auth.controllers import auth
from api.market.controllers import market
from api.me.controllers import me
from api.questions.controllers import questions
from api.common.errors.app_errors import AppErrors
from api.common.errors.error_handler import handle_error

class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(market, url_prefix='/market')
    app.register_blueprint(me, url_prefix='/me')
    app.register_blueprint(questions, url_prefix='/questions')
    app.register_error_handler(AppErrors, handle_error)

    migrate = Migrate(app, db)

    from api.seed import seed, clear
    app.cli.command('seed')(seed)
    app.cli.command('clear')(clear)

    return app
