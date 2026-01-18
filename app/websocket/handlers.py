"""
WebSocket event handlers for real-time messaging
"""
from flask_socketio import emit, disconnect
from flask_jwt_extended import decode_token
from app import db, socketio
from app.models.message import Message
from app.models.user import User

# Store active connections: {user_id: socket_id}
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
        print(f"Socket authentication error: {e}")
        return None


@socketio.on('connect')
def handle_connect(auth):
    """Handle WebSocket connection"""
    try:
        # Get token from auth parameter
        token = auth.get('token') if auth else None
        
        user_id = authenticate_socket(token)
        
        if not user_id:
            print("Unauthorized WebSocket connection attempt")
            disconnect()
            return False
        
        # Store connection
        from flask_socketio import request as ws_request
        active_connections[user_id] = ws_request.sid
        
        print(f"User {user_id} connected with socket {ws_request.sid}")
        
        emit('connected', {
            'success': True,
            'message': 'Connected to chat server',
            'userId': user_id
        })
        
        return True
        
    except Exception as e:
        print(f"Connection error: {e}")
        disconnect()
        return False


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    try:
        from flask_socketio import request as ws_request
        
        # Remove connection
        user_id = None
        for uid, sid in list(active_connections.items()):
            if sid == ws_request.sid:
                user_id = uid
                del active_connections[uid]
                break
        
        if user_id:
            print(f"User {user_id} disconnected")
        
    except Exception as e:
        print(f"Disconnection error: {e}")


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
        from flask_socketio import request as ws_request
        
        # Find sender from active connections
        sender_id = None
        for uid, sid in active_connections.items():
            if sid == ws_request.sid:
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
            print(f"Message delivered to user {receiver_id}")
        else:
            print(f"User {receiver_id} is offline, message saved")
        
    except Exception as e:
        print(f"Error handling message: {e}")
        db.session.rollback()
        emit('error', {
            'success': False,
            'message': 'Failed to send message'
        })


@socketio.on_error_default
def default_error_handler(e):
    """Handle WebSocket errors"""
    print(f"WebSocket error: {e}")
    emit('error', {
        'success': False,
        'message': 'An error occurred'
    })
