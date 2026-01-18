"""
WebSocket event handlers for real-time messaging
"""
import logging
from flask import request
from flask_socketio import emit, disconnect
from flask_jwt_extended import decode_token
from app import db, socketio
from app.models.message import Message
from app.models.user import User

# Configure logging
logger = logging.getLogger(__name__)

# Store active connections: {user_id: socket_id}
# Note: For production with multiple server instances, use Redis or similar
active_connections = {}


def authenticate_socket(token):
    """
    Authenticate WebSocket connection using JWT token
    Returns user_id if valid, None otherwise
    """
    try:
        if not token:
            return None
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        decoded = decode_token(token)
        user_id = decoded.get('sub')
        
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            return None
        
        return user_id
    except Exception as e:
        logger.warning(f"Socket authentication failed: {type(e).__name__}")
        return None


@socketio.on('connect')
def handle_connect(auth):
    """Handle WebSocket connection"""
    try:
        # Get token from auth parameter
        token = auth.get('token') if auth else None
        
        user_id = authenticate_socket(token)
        
        if not user_id:
            logger.warning("Unauthorized WebSocket connection attempt")
            disconnect()
            return False
        
        # Store connection
        active_connections[user_id] = request.sid
        
        logger.info(f"User {user_id} connected with socket {request.sid}")
        
        emit('connected', {
            'success': True,
            'message': 'Connected to chat server',
            'userId': user_id
        })
        
        return True
        
    except Exception as e:
        logger.error(f"Connection error: {type(e).__name__}")
        disconnect()
        return False


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    try:
        # Remove connection
        user_id = None
        for uid, sid in list(active_connections.items()):
            if sid == request.sid:
                user_id = uid
                del active_connections[uid]
                break
        
        if user_id:
            logger.info(f"User {user_id} disconnected")
        
    except Exception as e:
        logger.error(f"Disconnection error: {type(e).__name__}")


@socketio.on('send_message')
def handle_send_message(data):
    """
    Handle incoming message from client
    Expected data:
    {
        "receiverId": int,
        "content": str
    }
    """
    try:
        # Find sender from active connections
        sender_id = None
        for uid, sid in active_connections.items():
            if sid == request.sid:
                sender_id = uid
                break
        
        if not sender_id:
            emit('error', {
                'success': False,
                'message': 'Unauthorized'
            })
            return
        
        # Validate input
        receiver_id = data.get('receiverId')
        content = data.get('content')
        
        if not receiver_id or not content:
            emit('error', {
                'success': False,
                'message': 'Receiver ID and content are required'
            })
            return
        
        if not isinstance(content, str) or len(content.strip()) == 0:
            emit('error', {
                'success': False,
                'message': 'Message content cannot be empty'
            })
            return
        
        if len(content) > 5000:
            emit('error', {
                'success': False,
                'message': 'Message content too long (max 5000 characters)'
            })
            return
        
        # Check if receiver exists
        receiver = User.query.get(receiver_id)
        if not receiver:
            emit('error', {
                'success': False,
                'message': 'Receiver not found'
            })
            return
        
        # Create and save message
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content.strip()
        )
        
        db.session.add(message)
        db.session.commit()
        
        message_dict = message.to_dict()
        
        # Send acknowledgment to sender
        emit('message_sent', {
            'success': True,
            'message': message_dict
        })
        
        # Send message to receiver if online
        if receiver_id in active_connections:
            receiver_sid = active_connections[receiver_id]
            emit('receive_message', {
                'success': True,
                'message': message_dict
            }, room=receiver_sid)
            logger.info(f"Message delivered from user {sender_id} to user {receiver_id}")
        else:
            logger.info(f"User {receiver_id} is offline, message saved")
        
    except Exception as e:
        logger.error(f"Error handling message: {type(e).__name__}")
        db.session.rollback()
        emit('error', {
            'success': False,
            'message': 'Failed to send message'
        })


@socketio.on_error_default
def default_error_handler(e):
    """Handle WebSocket errors"""
    logger.error(f"WebSocket error: {type(e).__name__}")
    emit('error', {
        'success': False,
        'message': 'An error occurred'
    })
