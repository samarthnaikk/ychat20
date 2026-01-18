const User = require('../models/User');

class UserController {
  static async getProfile(req, res) {
    try {
      const user = await User.findById(req.user.id);
      
      if (!user) {
        return res.status(404).json({
          error: 'User not found',
          message: 'User profile not found'
        });
      }
      
      res.json({
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          full_name: user.full_name,
          bio: user.bio,
          created_at: user.created_at,
          updated_at: user.updated_at
        }
      });
    } catch (error) {
      console.error('Get profile error:', error);
      res.status(500).json({
        error: 'Failed to fetch profile',
        message: 'An error occurred while fetching profile'
      });
    }
  }

  static async updateProfile(req, res) {
    try {
      const { full_name, bio } = req.body;
      
      if (!full_name && !bio) {
        return res.status(400).json({
          error: 'Validation error',
          message: 'At least one field (full_name or bio) must be provided'
        });
      }
      
      const updatedUser = await User.updateProfile(req.user.id, {
        full_name,
        bio
      });
      
      res.json({
        message: 'Profile updated successfully',
        user: {
          id: updatedUser.id,
          username: updatedUser.username,
          email: updatedUser.email,
          full_name: updatedUser.full_name,
          bio: updatedUser.bio,
          updated_at: updatedUser.updated_at
        }
      });
    } catch (error) {
      console.error('Update profile error:', error);
      res.status(500).json({
        error: 'Failed to update profile',
        message: 'An error occurred while updating profile'
      });
    }
  }
}

module.exports = UserController;
