const pool = require('../config/database');

class Message {
  static async create({ sender_id, receiver_id, content }) {
    const query = `
      INSERT INTO messages (sender_id, receiver_id, content)
      VALUES ($1, $2, $3)
      RETURNING id, sender_id, receiver_id, content, created_at
    `;
    
    const values = [sender_id, receiver_id, content];
    const result = await pool.query(query, values);
    return result.rows[0];
  }

  static async getChatHistory(user1_id, user2_id, limit = 50, offset = 0) {
    const query = `
      SELECT 
        m.id,
        m.sender_id,
        m.receiver_id,
        m.content,
        m.created_at,
        m.read_at,
        u.username as sender_username
      FROM messages m
      JOIN users u ON m.sender_id = u.id
      WHERE (m.sender_id = $1 AND m.receiver_id = $2)
         OR (m.sender_id = $2 AND m.receiver_id = $1)
      ORDER BY m.created_at DESC
      LIMIT $3 OFFSET $4
    `;
    
    const values = [user1_id, user2_id, limit, offset];
    const result = await pool.query(query, values);
    return result.rows;
  }

  static async markAsRead(messageIds, userId) {
    const query = `
      UPDATE messages
      SET read_at = CURRENT_TIMESTAMP
      WHERE id = ANY($1) AND receiver_id = $2 AND read_at IS NULL
      RETURNING id
    `;
    
    const values = [messageIds, userId];
    const result = await pool.query(query, values);
    return result.rows;
  }
}

module.exports = Message;
