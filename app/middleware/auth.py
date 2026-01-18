"""
Authentication middleware and decorators
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User


def token_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            # Get user from database
            user = User.query.get(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 401
            
            return f(user, *args, **kwargs)
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Not authorized to access this route'
            }), 401
    
    return decorated_function
