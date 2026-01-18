"""
Room routes for group chat functionality
"""
import logging
from flask import Blueprint, request, jsonify
from app import db, limiter
from app.models.room import Room, RoomMember
from app.models.user import User
from app.models.message import Message
from app.middleware.auth import token_required

room_bp = Blueprint('rooms', __name__)
logger = logging.getLogger(__name__)


@room_bp.route('', methods=['POST'])
@limiter.limit("100 per 15 minutes")
@token_required
def create_room(current_user):
    """
    Create a new chat room
    POST /api/rooms
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required'
            }), 400
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({
                'success': False,
                'message': 'Room name is required'
            }), 400
        
        if len(name) > 100:
            return jsonify({
                'success': False,
                'message': 'Room name must not exceed 100 characters'
            }), 400
        
        # Create room
        room = Room(
            name=name,
            description=description if description else None,
            creator_id=current_user.id
        )
        
        db.session.add(room)
        db.session.flush()  # Get room ID
        
        # Add creator as first member
        member = RoomMember(
            room_id=room.id,
            user_id=current_user.id
        )
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Room created successfully',
            'data': {
                'room': room.to_dict()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating room: {type(e).__name__}")
        return jsonify({
            'success': False,
            'message': 'Server error while creating room'
        }), 500


@room_bp.route('', methods=['GET'])
@limiter.limit("100 per 15 minutes")
@token_required
def get_user_rooms(current_user):
    """
    Get all rooms the current user is a member of
    GET /api/rooms
    """
    try:
        # Get all room memberships for the user
        memberships = RoomMember.query.filter_by(user_id=current_user.id).all()
        room_ids = [m.room_id for m in memberships]
        
        # Get room details
        rooms = Room.query.filter(Room.id.in_(room_ids)).all() if room_ids else []
        
        return jsonify({
            'success': True,
            'data': {
                'rooms': [room.to_dict() for room in rooms]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching rooms: {type(e).__name__}")
        return jsonify({
            'success': False,
            'message': 'Server error while fetching rooms'
        }), 500


@room_bp.route('/<int:room_id>', methods=['GET'])
@limiter.limit("100 per 15 minutes")
@token_required
def get_room(current_user, room_id):
    """
    Get details of a specific room
    GET /api/rooms/:roomId
    """
    try:
        # Check if room exists
        room = Room.query.get(room_id)
        if not room:
            return jsonify({
                'success': False,
                'message': 'Room not found'
            }), 404
        
        # Check if user is a member
        membership = RoomMember.query.filter_by(
            room_id=room_id,
            user_id=current_user.id
        ).first()
        
        if not membership:
            return jsonify({
                'success': False,
                'message': 'Not authorized to access this room'
            }), 403
        
        # Get members
        members = RoomMember.query.filter_by(room_id=room_id).all()
        member_users = User.query.filter(
            User.id.in_([m.user_id for m in members])
        ).all()
        
        return jsonify({
            'success': True,
            'data': {
                'room': room.to_dict(),
                'members': [user.to_dict() for user in member_users]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching room: {type(e).__name__}")
        return jsonify({
            'success': False,
            'message': 'Server error while fetching room'
        }), 500


@room_bp.route('/<int:room_id>/members', methods=['POST'])
@limiter.limit("100 per 15 minutes")
@token_required
def add_room_member(current_user, room_id):
    """
    Add a user to a room
    POST /api/rooms/:roomId/members
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required'
            }), 400
        
        user_id = data.get('userId')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User ID is required'
            }), 400
        
        # Check if room exists
        room = Room.query.get(room_id)
        if not room:
            return jsonify({
                'success': False,
                'message': 'Room not found'
            }), 404
        
        # Check if current user is a member (only members can add others)
        current_membership = RoomMember.query.filter_by(
            room_id=room_id,
            user_id=current_user.id
        ).first()
        
        if not current_membership:
            return jsonify({
                'success': False,
                'message': 'Not authorized to add members to this room'
            }), 403
        
        # Check if user to add exists
        user_to_add = User.query.get(user_id)
        if not user_to_add:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Check if user is already a member
        existing_membership = RoomMember.query.filter_by(
            room_id=room_id,
            user_id=user_id
        ).first()
        
        if existing_membership:
            return jsonify({
                'success': False,
                'message': 'User is already a member of this room'
            }), 400
        
        # Add member
        member = RoomMember(
            room_id=room_id,
            user_id=user_id
        )
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Member added successfully',
            'data': {
                'member': member.to_dict()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding room member: {type(e).__name__}")
        return jsonify({
            'success': False,
            'message': 'Server error while adding member'
        }), 500


@room_bp.route('/<int:room_id>/members/<int:user_id>', methods=['DELETE'])
@limiter.limit("100 per 15 minutes")
@token_required
def remove_room_member(current_user, room_id, user_id):
    """
    Remove a user from a room
    DELETE /api/rooms/:roomId/members/:userId
    """
    try:
        # Check if room exists
        room = Room.query.get(room_id)
        if not room:
            return jsonify({
                'success': False,
                'message': 'Room not found'
            }), 404
        
        # Users can remove themselves, or room creator can remove others
        if user_id != current_user.id and room.creator_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Not authorized to remove this member'
            }), 403
        
        # Find membership
        membership = RoomMember.query.filter_by(
            room_id=room_id,
            user_id=user_id
        ).first()
        
        if not membership:
            return jsonify({
                'success': False,
                'message': 'User is not a member of this room'
            }), 404
        
        # Don't allow removing the creator if they're the last member
        members_count = RoomMember.query.filter_by(room_id=room_id).count()
        if user_id == room.creator_id and members_count > 1:
            return jsonify({
                'success': False,
                'message': 'Room creator cannot leave while other members are present'
            }), 400
        
        db.session.delete(membership)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Member removed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error removing room member: {type(e).__name__}")
        return jsonify({
            'success': False,
            'message': 'Server error while removing member'
        }), 500


@room_bp.route('/<int:room_id>/messages', methods=['GET'])
@limiter.limit("100 per 15 minutes")
@token_required
def get_room_messages(current_user, room_id):
    """
    Get messages in a room
    GET /api/rooms/:roomId/messages
    Query params:
    - page: Page number (default: 1)
    - per_page: Results per page (default: 50, max: 100)
    """
    try:
        # Check if room exists
        room = Room.query.get(room_id)
        if not room:
            return jsonify({
                'success': False,
                'message': 'Room not found'
            }), 404
        
        # Check if user is a member
        membership = RoomMember.query.filter_by(
            room_id=room_id,
            user_id=current_user.id
        ).first()
        
        if not membership:
            return jsonify({
                'success': False,
                'message': 'Not authorized to access this room'
            }), 403
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        if page < 1 or per_page < 1:
            return jsonify({
                'success': False,
                'message': 'Invalid pagination parameters'
            }), 400
        
        # Query messages for the room
        messages_query = Message.query.filter_by(
            room_id=room_id
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
        logger.error(f"Error fetching room messages: {type(e).__name__}")
        return jsonify({
            'success': False,
            'message': 'Server error while fetching messages'
        }), 500
