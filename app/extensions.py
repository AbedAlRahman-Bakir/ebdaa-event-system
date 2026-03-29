"""Flask extensions initialization."""

from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def init_extensions(app):
    """Register all extensions with the Flask app instance."""
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
