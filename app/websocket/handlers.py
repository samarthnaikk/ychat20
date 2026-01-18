"""
WebSocket event handlers for real-time messaging
"""
import logging
from datetime import datetime
from flask import request
from flask_socketio import emit, disconnect, join_room, leave_room
from flask_jwt_extended import decode_token
from app import db, socketio
from app.models.message import Message
from app.models.user import User
from app.models.room import Room, RoomMember

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
            logger.debug("No token provided for socket authentication")
            return None
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        decoded = decode_token(token)
        user_id = decoded.get('sub')
        
        if not user_id:
            logger.warning("Token decoded but no user_id found in sub claim")
            return None
        
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            logger.warning(f"Token valid but user {user_id} not found in database")
            return None
        
        logger.debug(f"Socket authentication successful for user {user_id}")
        return user_id
    except Exception as e:
        logger.warning(f"Socket authentication failed: {type(e).__name__}: {str(e)}")
        return None


@socketio.on('connect')
def handle_connect(auth):
    """Handle WebSocket connection"""
    try:
        # Get token from auth parameter
        token = auth.get('token') if auth else None
        
        if not token:
            logger.warning("WebSocket connection attempted without token")
            emit('error', {
                'success': False,
                'message': 'Authentication token required'
            })
            return False
        
        user_id = authenticate_socket(token)
        
        if not user_id:
            logger.warning("Unauthorized WebSocket connection attempt - invalid token")
            emit('error', {
                'success': False,
                'message': 'Invalid or expired token'
            })
            return False
        
        # Store connection
        active_connections[user_id] = request.sid
        
        # Join user to their rooms
        memberships = RoomMember.query.filter_by(user_id=user_id).all()
        for membership in memberships:
            join_room(f"room_{membership.room_id}")
        
        logger.info(f"User {user_id} connected with socket {request.sid}")
        
        emit('connected', {
            'success': True,
            'message': 'Connected to chat server',
            'userId': user_id
        })
        
        return True
        
    except Exception as e:
        logger.error(f"Connection error: {type(e).__name__}: {str(e)}")
        emit('error', {
            'success': False,
            'message': 'Connection failed'
        })
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


@socketio.on('send_room_message')
def handle_send_room_message(data):
    """
    Handle incoming room message from client
    Expected data:
    {
        "roomId": int,
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
        room_id = data.get('roomId')
        content = data.get('content')
        
        if not room_id or not content:
            emit('error', {
                'success': False,
                'message': 'Room ID and content are required'
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
        
        # Check if room exists
        room = Room.query.get(room_id)
        if not room:
            emit('error', {
                'success': False,
                'message': 'Room not found'
            })
            return
        
        # Check if sender is a member
        membership = RoomMember.query.filter_by(
            room_id=room_id,
            user_id=sender_id
        ).first()
        
        if not membership:
            emit('error', {
                'success': False,
                'message': 'Not authorized to send messages to this room'
            })
            return
        
        # Create and save message
        message = Message(
            sender_id=sender_id,
            room_id=room_id,
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
        
        # Broadcast to all room members
        emit('receive_room_message', {
            'success': True,
            'message': message_dict
        }, room=f"room_{room_id}", skip_sid=request.sid)
        
        logger.info(f"Room message from user {sender_id} to room {room_id}")
        
    except Exception as e:
        logger.error(f"Error handling room message: {type(e).__name__}")
        db.session.rollback()
        emit('error', {
            'success': False,
            'message': 'Failed to send room message'
        })


@socketio.on('edit_message')
def handle_edit_message(data):
    """
    Handle message edit request
    Expected data:
    {
        "messageId": int,
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
        
        message_id = data.get('messageId')
        content = data.get('content')
        
        if not message_id or not content:
            emit('error', {
                'success': False,
                'message': 'Message ID and content are required'
            })
            return
        
        if len(content.strip()) == 0 or len(content) > 5000:
            emit('error', {
                'success': False,
                'message': 'Invalid content length'
            })
            return
        
        # Find message
        message = Message.query.get(message_id)
        if not message or message.sender_id != sender_id:
            emit('error', {
                'success': False,
                'message': 'Message not found or not authorized'
            })
            return
        
        if message.deleted_at:
            emit('error', {
                'success': False,
                'message': 'Cannot edit deleted message'
            })
            return
        
        # Update message
        message.content = content.strip()
        message.edited_at = datetime.utcnow()
        db.session.commit()
        
        message_dict = message.to_dict()
        
        # Notify sender
        emit('message_edited', {
            'success': True,
            'message': message_dict
        })
        
        # Notify receiver or room
        if message.room_id:
            emit('message_edited', {
                'success': True,
                'message': message_dict
            }, room=f"room_{message.room_id}", skip_sid=request.sid)
        elif message.receiver_id and message.receiver_id in active_connections:
            receiver_sid = active_connections[message.receiver_id]
            emit('message_edited', {
                'success': True,
                'message': message_dict
            }, room=receiver_sid)
        
    except Exception as e:
        logger.error(f"Error editing message: {type(e).__name__}")
        db.session.rollback()
        emit('error', {
            'success': False,
            'message': 'Failed to edit message'
        })


@socketio.on('delete_message')
def handle_delete_message(data):
    """
    Handle message delete request
    Expected data:
    {
        "messageId": int
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
        
        message_id = data.get('messageId')
        
        if not message_id:
            emit('error', {
                'success': False,
                'message': 'Message ID is required'
            })
            return
        
        # Find message
        message = Message.query.get(message_id)
        if not message or message.sender_id != sender_id:
            emit('error', {
                'success': False,
                'message': 'Message not found or not authorized'
            })
            return
        
        if message.deleted_at:
            emit('error', {
                'success': False,
                'message': 'Message already deleted'
            })
            return
        
        # Soft delete
        message.deleted_at = datetime.utcnow()
        db.session.commit()
        
        message_dict = message.to_dict()
        
        # Notify sender
        emit('message_deleted', {
            'success': True,
            'message': message_dict
        })
        
        # Notify receiver or room
        if message.room_id:
            emit('message_deleted', {
                'success': True,
                'message': message_dict
            }, room=f"room_{message.room_id}", skip_sid=request.sid)
        elif message.receiver_id and message.receiver_id in active_connections:
            receiver_sid = active_connections[message.receiver_id]
            emit('message_deleted', {
                'success': True,
                'message': message_dict
            }, room=receiver_sid)
        
    except Exception as e:
        logger.error(f"Error deleting message: {type(e).__name__}")
        db.session.rollback()
        emit('error', {
            'success': False,
            'message': 'Failed to delete message'
        })


@socketio.on_error_default
def default_error_handler(e):
    """Handle WebSocket errors"""
    logger.error(f"WebSocket error: {type(e).__name__}")
    emit('error', {
        'success': False,
        'message': 'An error occurred'
    })
