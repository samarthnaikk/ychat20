"""
Message routes for chat history
"""
import logging
from flask import Blueprint, request, jsonify
from app import db, limiter
from app.models.message import Message
from app.models.user import User
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
