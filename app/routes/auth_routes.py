"""
Authentication routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app import db, limiter
from app.models.user import User
from app.middleware.auth import token_required
from app.utils.validation import validate_registration_data, validate_login_data, validate_profile_update_data

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("1000 per 15 minutes")
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
@limiter.limit("1000 per 15 minutes")
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


@auth_bp.route('/profile', methods=['PUT'])
@limiter.limit("100 per 15 minutes")
@token_required
def update_profile(user):
    """
    Update current user profile
    PUT /api/auth/profile
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required'
            }), 400
        
        # Validate input
        errors, username, email = validate_profile_update_data(data)
        
        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            }), 400
        
        # Check if username or email already taken by another user
        if username is not None and username != user.username:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return jsonify({
                    'success': False,
                    'message': 'Username already taken'
                }), 400
            user.username = username
        
        if email is not None and email != user.email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({
                    'success': False,
                    'message': 'Email already registered'
                }), 400
            user.email = email
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'data': {
                'user': user.to_dict()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Server error during profile update'
        }), 500


@auth_bp.route('/users/search', methods=['GET'])
@limiter.limit("100 per 15 minutes")
@token_required
def search_users(user):
    """
    Search for users by username
    GET /api/auth/users/search?q=username
    """
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'message': 'Search query is required'
            }), 400
        
        if len(query) < 2:
            return jsonify({
                'success': False,
                'message': 'Search query must be at least 2 characters'
            }), 400
        
        # Search users by username (case-insensitive)
        users = User.query.filter(
            User.username.ilike(f'%{query}%'),
            User.id != user.id  # Exclude current user
        ).limit(10).all()
        
        return jsonify({
            'success': True,
            'data': {
                'users': [u.to_dict() for u in users],
                'query': query
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Server error during user search'
        }), 500
