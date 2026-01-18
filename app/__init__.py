"""
Initialize Flask application and extensions
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from app.config.settings import config

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
socketio = SocketIO()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per 15 minutes"]
)


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Validate production settings
    config[config_name].validate_production()
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    limiter.init_app(app)
    socketio.init_app(app, cors_allowed_origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.message_routes import message_bp
    from app.routes.room_routes import room_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(message_bp, url_prefix='/api/messages')
    app.register_blueprint(room_bp, url_prefix='/api/rooms')
    
    # Register WebSocket handlers
    from app.websocket import handlers
    
    # Root route
    @app.route('/')
    def index():
        return {
            'message': 'YChat20 API',
            'version': '1.0.0',
            'endpoints': {
                'register': 'POST /api/auth/register',
                'login': 'POST /api/auth/login',
                'me': 'GET /api/auth/me (Protected)',
                'chatHistory': 'GET /api/messages/history/:userId (Protected)'
            },
            'websocket': {
                'connect': 'WebSocket connection with JWT auth',
                'events': {
                    'send_message': 'Send a message to another user',
                    'receive_message': 'Receive messages from other users',
                    'connected': 'Connection acknowledgment',
                    'message_sent': 'Message delivery confirmation'
                }
            }
        }
    
    # 404 handler
    @app.errorhandler(404)
    def not_found(error):
        return {'success': False, 'message': 'Route not found'}, 404
    
    # 500 handler
    @app.errorhandler(500)
    def internal_error(error):
        return {'success': False, 'message': 'Internal server error'}, 500
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
