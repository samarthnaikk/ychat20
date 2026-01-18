const { verifyToken } = require('../utils/jwt');
const User = require('../models/User');

async function authenticate(req, res, next) {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        error: 'Authentication required',
        message: 'Please provide a valid authentication token'
      });
    }
    
    const token = authHeader.substring(7);
    const decoded = verifyToken(token);
    
    if (!decoded) {
      return res.status(401).json({
        error: 'Invalid token',
        message: 'Authentication token is invalid or expired'
      });
    }
    
    const user = await User.findById(decoded.userId);
    
    if (!user) {
      return res.status(401).json({
        error: 'User not found',
        message: 'User associated with token no longer exists'
      });
    }
    
    req.user = user;
    next();
  } catch (error) {
    console.error('Authentication error:', error);
    res.status(500).json({
      error: 'Authentication failed',
      message: 'An error occurred during authentication'
    });
  }
}

module.exports = authenticate;
