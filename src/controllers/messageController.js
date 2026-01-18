const Message = require('../models/Message');
const User = require('../models/User');

class MessageController {
  static async getChatHistory(req, res) {
    try {
      const { userId } = req.params;
      const { limit = 50, offset = 0 } = req.query;
      
      if (!userId || isNaN(userId)) {
        return res.status(400).json({
          error: 'Validation error',
          message: 'Valid user ID is required'
        });
      }
      
      const otherUser = await User.findById(userId);
      if (!otherUser) {
        return res.status(404).json({
          error: 'User not found',
          message: 'The specified user does not exist'
        });
      }
      
      const messages = await Message.getChatHistory(
        req.user.id,
        parseInt(userId),
        parseInt(limit),
        parseInt(offset)
      );
      
      res.json({
        messages: messages.reverse(),
        pagination: {
          limit: parseInt(limit),
          offset: parseInt(offset),
          total: messages.length
        }
      });
    } catch (error) {
      console.error('Get chat history error:', error);
      res.status(500).json({
        error: 'Failed to fetch chat history',
        message: 'An error occurred while fetching chat history'
      });
    }
  }
}

module.exports = MessageController;
