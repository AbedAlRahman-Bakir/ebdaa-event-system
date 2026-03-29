"""Global error handlers for consistent JSON error responses."""

from flask import jsonify


def register_error_handlers(app):
    """Register error handlers with the Flask app."""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(success=False, message="Bad request", errors=str(error)), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify(success=False, message="Unauthorized"), 401

    @app.errorhandler(404)
    def not_found(error):
        return jsonify(success=False, message="Resource not found"), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify(success=False, message="Method not allowed"), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify(success=False, message="Internal server error"), 500
