from flask import Flask, jsonify
from pydantic import ValidationError

from app.db import db
from app.routes import portfolio_bp, security_bp, trade_bp, user_bp


def create_app(config):
    try:
        app = Flask(__name__)
        app.config.from_object(config)

        # register extensions
        db.init_app(app)
        with app.app_context():
            db.create_all()

        # Initialize Flask-Caching
        from flask_caching import Cache
        cache = Cache(app, config={
            'CACHE_TYPE': 'SimpleCache',
            'CACHE_DEFAULT_TIMEOUT': 300
        })
        app.cache = cache

        # register blueprints
        app.register_blueprint(user_bp, url_prefix='/users')
        app.register_blueprint(portfolio_bp, url_prefix='/portfolios')
        app.register_blueprint(security_bp, url_prefix='/securities')
        app.register_blueprint(trade_bp, url_prefix='/trades')

        # Centralized error handler for generic exceptions
        @app.errorhandler(Exception)
        def handle_exception(e):
            return jsonify({
                "error": "Internal Server Error",
                "detail": str(e)
            }), 500

        # Centralized error handler for Pydantic ValidationError
        @app.errorhandler(ValidationError)
        def handle_validation_error(e):
            return jsonify({
                "error": "Validation Error",
                "detail": e.errors()
            }), 422

        return app
    except Exception as e:
        print(f'Error creating app: {e}')
        raise
