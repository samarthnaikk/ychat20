"""
Message routes for chat history
"""
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db, limiter
from app.models.message import Message
from app.models.user import User
from app.models.room import RoomMember
from app.middleware.auth import token_required

message_bp = Blueprint('messages', __name__)
logger = logging.getLogger(__name__)


@message_bp.route('/history/<int:user_id>', methods=['GET'])
@limiter.limit("100 per 15 minutes")
@token_required
def get_chat_history(current_user, user_id):
    """
    Get chat history between current user and another user
    GET /api/messages/history/:userId
    Query params:
    - page: Page number (default: 1)
    - per_page: Results per page (default: 50, max: 100)
    """
    try:
        # Check if the other user exists
        other_user = User.query.get(user_id)
        if not other_user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        if page < 1 or per_page < 1:
            return jsonify({
                'success': False,
                'message': 'Invalid pagination parameters'
            }), 400
        
        # Query messages between the two users
        messages_query = Message.query.filter(
            db.or_(
                db.and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
                db.and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
            )
        ).order_by(Message.timestamp.asc())
        
        # Paginate results
        pagination = messages_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        messages = [message.to_dict() for message in pagination.items]
        
        return jsonify({
            'success': True,
            'data': {
                'messages': messages,
                'pagination': {
                    'page': pagination.page,
                    'perPage': pagination.per_page,
                    'totalPages': pagination.pages,
                    'totalMessages': pagination.total,
                    'hasNext': pagination.has_next,
                    'hasPrev': pagination.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching chat history: {type(e).__name__} - {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Server error while fetching messages'
        }), 500


@message_bp.route('/<int:message_id>', methods=['PUT'])
@limiter.limit("100 per 15 minutes")
@token_required
def edit_message(current_user, message_id):
    """
    Edit a message
    PUT /api/messages/:messageId
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required'
            }), 400
        
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({
                'success': False,
                'message': 'Content is required'
            }), 400
        
        if len(content) > 5000:
            return jsonify({
                'success': False,
                'message': 'Content too long (max 5000 characters)'
            }), 400
        
        # Find message
        message = Message.query.get(message_id)
        if not message:
            return jsonify({
                'success': False,
                'message': 'Message not found'
            }), 404
        
        # Check if user is the sender
        if message.sender_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Not authorized to edit this message'
            }), 403
        
        # Check if message is deleted
        if message.deleted_at:
            return jsonify({
                'success': False,
                'message': 'Cannot edit a deleted message'
            }), 400
        
        # Update message
        message.content = content
        message.edited_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Message edited successfully',
            'data': {
                'message': message.to_dict()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error editing message: {type(e).__name__}")
        return jsonify({
            'success': False,
            'message': 'Server error while editing message'
        }), 500


@message_bp.route('/<int:message_id>', methods=['DELETE'])
@limiter.limit("100 per 15 minutes")
@token_required
def delete_message(current_user, message_id):
    """
    Delete a message (soft delete - mark as deleted)
    DELETE /api/messages/:messageId
    """
    try:
        # Find message
        message = Message.query.get(message_id)
        if not message:
            return jsonify({
                'success': False,
                'message': 'Message not found'
            }), 404
        
        # Check if user is the sender
        if message.sender_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Not authorized to delete this message'
            }), 403
        
        # Check if message is already deleted
        if message.deleted_at:
            return jsonify({
                'success': False,
                'message': 'Message is already deleted'
            }), 400
        
        # Soft delete - mark as deleted
        message.deleted_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Message deleted successfully',
            'data': {
                'message': message.to_dict()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting message: {type(e).__name__}")
        return jsonify({
            'success': False,
            'message': 'Server error while deleting message'
        }), 500

