"""
Message model for chat persistence
"""
from datetime import datetime
from app import db


class Message(db.Model):
    """Message model for storing chat messages"""
    
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    edited_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    room = db.relationship('Room', backref='messages')
    
    def __repr__(self):
        if self.room_id:
            return f'<Message from {self.sender_id} to room {self.room_id}>'
        return f'<Message from {self.sender_id} to {self.receiver_id}>'
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'senderId': self.sender_id,
            'receiverId': self.receiver_id,
            'roomId': self.room_id,
            'content': self.content if not self.deleted_at else '[Message deleted]',
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'editedAt': self.edited_at.isoformat() if self.edited_at else None,
            'deletedAt': self.deleted_at.isoformat() if self.deleted_at else None,
            'isDeleted': self.deleted_at is not None,
            'isEdited': self.edited_at is not None
        }
