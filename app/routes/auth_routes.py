"""
Authentication routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app import db, limiter
from app.models.user import User
from app.middleware.auth import token_required
from app.utils.validation import validate_registration_data, validate_login_data

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per 15 minutes")
def register():
    """
    Register a new user
    POST /api/auth/register
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required'
            }), 400
        
        # Validate input
        errors, username, email, password = validate_registration_data(data)
        
        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            }), 400
        
        # Check for existing user
        existing_user = User.query.filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            if existing_user.email == email:
                return jsonify({
                    'success': False,
                    'message': 'Email already registered'
                }), 400
            if existing_user.username == username:
                return jsonify({
                    'success': False,
                    'message': 'Username already taken'
                }), 400
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate JWT token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'user': user.to_dict(),
                'token': access_token
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Server error during registration'
        }), 500


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per 15 minutes")
def login():
    """
    Login user
    POST /api/auth/login
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required'
            }), 400
        
        # Validate input
        errors, email, password = validate_login_data(data)
        
        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            }), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
        
        # Generate JWT token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': user.to_dict(),
                'token': access_token
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Server error during login'
        }), 500


@auth_bp.route('/me', methods=['GET'])
@limiter.limit("100 per 15 minutes")
@token_required
def get_me(user):
    """
    Get current logged in user
    GET /api/auth/me
    """
    try:
        return jsonify({
            'success': True,
            'data': {
                'user': user.to_dict()
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Server error'
        }), 500
