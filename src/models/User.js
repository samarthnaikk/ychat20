const pool = require('../config/database');
const bcrypt = require('bcryptjs');

class User {
  static async create({ username, email, password, full_name }) {
    const hashedPassword = await bcrypt.hash(password, 10);
    
    const query = `
      INSERT INTO users (username, email, password_hash, full_name)
      VALUES ($1, $2, $3, $4)
      RETURNING id, username, email, full_name, created_at
    `;
    
    const values = [username, email, hashedPassword, full_name];
    const result = await pool.query(query, values);
    return result.rows[0];
  }

  static async findByEmail(email) {
    const query = 'SELECT * FROM users WHERE email = $1';
    const result = await pool.query(query, [email]);
    return result.rows[0];
  }

  static async findByUsername(username) {
    const query = 'SELECT * FROM users WHERE username = $1';
    const result = await pool.query(query, [username]);
    return result.rows[0];
  }

  static async findById(id) {
    const query = `
      SELECT id, username, email, full_name, bio, created_at, updated_at
      FROM users WHERE id = $1
    `;
    const result = await pool.query(query, [id]);
    return result.rows[0];
  }

  static async updateProfile(id, { full_name, bio }) {
    const query = `
      UPDATE users
      SET full_name = COALESCE($1, full_name),
          bio = COALESCE($2, bio),
          updated_at = CURRENT_TIMESTAMP
      WHERE id = $3
      RETURNING id, username, email, full_name, bio, updated_at
    `;
    
    const values = [full_name, bio, id];
    const result = await pool.query(query, values);
    return result.rows[0];
  }

  static async verifyPassword(plainPassword, hashedPassword) {
    return bcrypt.compare(plainPassword, hashedPassword);
  }
}

module.exports = User;
