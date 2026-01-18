"""
Routes package
"""
from app.routes.auth_routes import auth_bp
from app.routes.message_routes import message_bp

__all__ = ["auth_bp", "message_bp"]
