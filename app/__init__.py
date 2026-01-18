"""
Initialize Flask application and extensions
"""
from flask import Flask, render_template, redirect, url_for
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
    import os
    import logging
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Get the parent directory of the app package for templates and static files
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Log JWT configuration for debugging
    logger.info(f"JWT_SECRET_KEY configured: {bool(app.config.get('JWT_SECRET_KEY'))}")
    logger.info(f"JWT_ACCESS_TOKEN_EXPIRES: {app.config.get('JWT_ACCESS_TOKEN_EXPIRES')}")
    
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
    
    # Root route - redirect to login page
    @app.route('/')
    def index():
        return render_template('login.html')
    
    # Chat page route
    @app.route('/chat')
    def chat():
        return render_template('chat.html')
    
    # API info route
    @app.route('/api')
    def api_info():
        return {
            'message': 'YChat20 API',
            'version': '1.0.0',
            'endpoints': {
                'register': 'POST /api/auth/register',
                'login': 'POST /api/auth/login',
                'me': 'GET /api/auth/me (Protected)',
                'updateProfile': 'PUT /api/auth/profile (Protected)',
                'chatHistory': 'GET /api/messages/history/:userId (Protected)',
                'editMessage': 'PUT /api/messages/:messageId (Protected)',
                'deleteMessage': 'DELETE /api/messages/:messageId (Protected)',
                'createRoom': 'POST /api/rooms (Protected)',
                'getRooms': 'GET /api/rooms (Protected)',
                'getRoom': 'GET /api/rooms/:roomId (Protected)',
                'addRoomMember': 'POST /api/rooms/:roomId/members (Protected)',
                'removeRoomMember': 'DELETE /api/rooms/:roomId/members/:userId (Protected)',
                'getRoomMessages': 'GET /api/rooms/:roomId/messages (Protected)'
            },
            'websocket': {
                'connect': 'WebSocket connection with JWT auth',
                'events': {
                    'send_message': 'Send a message to another user',
                    'receive_message': 'Receive messages from other users',
                    'send_room_message': 'Send a message to a room',
                    'receive_room_message': 'Receive room messages',
                    'edit_message': 'Edit a message',
                    'message_edited': 'Message edit notification',
                    'delete_message': 'Delete a message',
                    'message_deleted': 'Message delete notification',
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
