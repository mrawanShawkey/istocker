from flask import Flask, request
from flask_migrate import Migrate
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError, JWTDecodeError
from werkzeug.middleware.proxy_fix import ProxyFix

from api.config import Config
from api.common.extentions.extentions import db, bcrypt, jwt
from flask_cors import CORS
from api.auth.controllers import auth
from api.market.controllers import market
from api.user.controllers import user
from api.questions.controllers import questions
from api.recommendations.controllers import recommendations
from api.common.errors.app_errors import AppErrors
from api.common.errors.error_handler import handle_error

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Apply ProxyFix to handle X-Forwarded-* headers from Render/Cloudflare
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    
    # Handle HTTPS when behind a proxy (e.g., Render, AWS ELB)
    app.config['PREFERRED_URL_SCHEME'] = 'https'

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Enable CORS for all origins (convenient for testing). Restrict in prod.
    CORS(app, resources={r"/*": {"origins": "*"}})

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(market, url_prefix='/market')
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(questions, url_prefix='/questions')
    app.register_blueprint(recommendations, url_prefix='/recommendations')
    app.register_error_handler(AppErrors, handle_error)
    app.register_error_handler(NoAuthorizationError, handle_error)
    app.register_error_handler(InvalidHeaderError, handle_error)
    app.register_error_handler(JWTDecodeError, handle_error)

    migrate = Migrate(app, db)

    # Register seed/clear CLI commands if available. Importing seed may require
    # heavy optional dependencies (pandas, etc.), so import lazily and tolerate
    # failures in lightweight environments used for quick testing.
    try:
        from api.seed import seed, clear
        app.cli.command('seed')(seed)
        app.cli.command('clear')(clear)
    except Exception:
        pass

    # Ensure CORS headers are present on all responses (safety net)
    @app.after_request
    def _add_cors_headers(response):
        origin = request.headers.get('Origin')
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        else:
            response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        return response

    # Handle automatic OPTIONS responses from Werkzeug so they include CORS headers
    @app.before_request
    def _handle_options():
        if request.method == 'OPTIONS':
            resp = app.make_default_options_response()
            origin = request.headers.get('Origin')
            if origin:
                resp.headers['Access-Control-Allow-Origin'] = origin
            else:
                resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Access-Control-Allow-Credentials'] = 'true'
            resp.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
            resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
            return resp

    return app
