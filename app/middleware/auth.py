"""
Authentication middleware and decorators
"""
import logging
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User

logger = logging.getLogger(__name__)


def token_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Log the incoming request headers for debugging
            auth_header = request.headers.get('Authorization', 'No Authorization header')
            logger.info(f"Auth attempt - Authorization header: {auth_header[:50] if len(auth_header) > 50 else auth_header}")
            
            verify_jwt_in_request()
            user_id_str = get_jwt_identity()
            user_id = int(user_id_str)  # Convert string back to integer
            
            logger.info(f"JWT verified successfully - User ID: {user_id}")
            
            # Get user from database
            user = User.query.get(user_id)
            if not user:
                logger.warning(f"User not found in database: {user_id}")
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 401
            
            logger.info(f"User found: {user.username}")
            return f(user, *args, **kwargs)
        except Exception as e:
            logger.error(f"Authentication failed: {type(e).__name__}: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Not authorized to access this route'
            }), 401
    
    return decorated_function
