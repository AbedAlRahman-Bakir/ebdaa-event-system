"""Admin user model for authentication and authorization."""

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class AdminUser(db.Model):
    """Represents admin and check-in operator accounts."""

    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'operator'

    def set_password(self, password):
        """Hash and store the password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Serialize admin user to dictionary (excludes password)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
        }
