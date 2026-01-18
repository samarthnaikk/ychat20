"""
Input validation utilities
"""
import re
from email_validator import validate_email, EmailNotValidError


def validate_username(username):
    """Validate username format and length"""
    errors = []
    
    if not username:
        errors.append('Username is required')
        return errors
    
    if len(username) < 3:
        errors.append('Username must be at least 3 characters long')
    
    if len(username) > 30:
        errors.append('Username must not exceed 30 characters')
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        errors.append('Username can only contain letters, numbers, and underscores')
    
    return errors


def validate_email_format(email):
    """Validate email format"""
    errors = []
    
    if not email:
        errors.append('Email is required')
        return errors
    
    try:
        # Validate and normalize email
        validated = validate_email(email, check_deliverability=False)
        return errors
    except EmailNotValidError as e:
        errors.append('Please provide a valid email address')
        return errors


def validate_password(password):
    """Validate password strength"""
    errors = []
    
    if not password:
        errors.append('Password is required')
        return errors
    
    if len(password) < 6:
        errors.append('Password must be at least 6 characters long')
    
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter')
    
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter')
    
    if not re.search(r'\d', password):
        errors.append('Password must contain at least one number')
    
    return errors


def validate_registration_data(data):
    """Validate registration request data"""
    all_errors = []
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    all_errors.extend(validate_username(username))
    all_errors.extend(validate_email_format(email))
    all_errors.extend(validate_password(password))
    
    return all_errors, username, email, password


def validate_login_data(data):
    """Validate login request data"""
    errors = []
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email:
        errors.append('Email is required')
    
    if not password:
        errors.append('Password is required')
    
    return errors, email, password
