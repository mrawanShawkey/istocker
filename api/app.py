from flask import Flask
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from api.config import Config

class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)

    db.init_app(app)

    from api.routes import register_routes
    register_routes(app, db)

    migrate = Migrate(app, db)

    from api.seed import seed
    app.cli.command('seed')(seed)

    return app
