"""Application factory."""

from flask import Flask

from app.extensions import init_extensions
from config import get_config


def create_app():
    """Create and configure the Flask application."""

    app = Flask(__name__)
    config = get_config()
    app.config.from_object(config)

    init_extensions(app)

    from app.errors import register_error_handlers

    register_error_handlers(app)

    from app import models  # noqa: F401 — so Migrate detects all tables
    from app.routes.attendance import attendance_bp

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.main import main_bp
    from app.routes.users import users_bp
    from app.routes.visitors import visitors_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(visitors_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(main_bp)

    # JWT token blacklist check
    from app.extensions import jwt
    from app.routes.auth import blacklisted_tokens

    @jwt.token_in_blocklist_loader
    def check_token_blacklist(_jwt_header, jwt_payload):
        return jwt_payload["jti"] in blacklisted_tokens

    # Register CLI commands
    from app.commands import seed_admin, seed_slots

    app.cli.add_command(seed_admin)
    app.cli.add_command(seed_slots)

    return app
