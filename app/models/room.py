"""
Room model for group chats
"""
from datetime import datetime
from app import db


class Room(db.Model):
    """Room model for group chat functionality"""
    
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[creator_id], backref='created_rooms')
    members = db.relationship('RoomMember', back_populates='room', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Room {self.name}>'
    
    def to_dict(self):
        """Convert room to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'creatorId': self.creator_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


class RoomMember(db.Model):
    """RoomMember model for tracking room membership"""
    
    __tablename__ = 'room_members'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    room = db.relationship('Room', back_populates='members')
    user = db.relationship('User', backref='room_memberships')
    
    # Unique constraint - a user can only be a member of a room once
    __table_args__ = (
        db.UniqueConstraint('room_id', 'user_id', name='unique_room_member'),
    )
    
    def __repr__(self):
        return f'<RoomMember user={self.user_id} room={self.room_id}>'
    
    def to_dict(self):
        """Convert room member to dictionary"""
        return {
            'id': self.id,
            'roomId': self.room_id,
            'userId': self.user_id,
            'joinedAt': self.joined_at.isoformat() if self.joined_at else None
        }
