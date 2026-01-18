const jwt = require('jsonwebtoken');

/**
 * Get JWT secret from environment variables
 * @returns {string} JWT secret
 * @throws {Error} If JWT_SECRET is not set in production
 */
const getJwtSecret = () => {
  const secret = process.env.JWT_SECRET;
  
  if (!secret && process.env.NODE_ENV === 'production') {
    throw new Error('JWT_SECRET must be set in production environment');
  }
  
  return secret || 'your-secret-key-change-this-in-production';
};

/**
 * Generate JWT token for a user
 * @param {string} userId - User ID to embed in token
 * @returns {string} JWT token
 */
const generateToken = (userId) => {
  return jwt.sign(
    { id: userId },
    getJwtSecret(),
    { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
  );
};

/**
 * Verify JWT token
 * @param {string} token - JWT token to verify
 * @returns {object} Decoded token payload
 */
const verifyToken = (token) => {
  try {
    return jwt.verify(token, getJwtSecret());
  } catch (error) {
    throw new Error('Invalid or expired token');
  }
};

module.exports = {
  generateToken,
  verifyToken
};
