const User = require('../models/User');
const { generateToken } = require('../utils/jwt');

class AuthController {
  static async register(req, res) {
    try {
      const { username, email, password, full_name } = req.body;
      
      if (!username || !email || !password) {
        return res.status(400).json({
          error: 'Validation error',
          message: 'Username, email, and password are required'
        });
      }
      
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        return res.status(400).json({
          error: 'Validation error',
          message: 'Invalid email format'
        });
      }
      
      if (password.length < 6) {
        return res.status(400).json({
          error: 'Validation error',
          message: 'Password must be at least 6 characters long'
        });
      }
      
      const existingUser = await User.findByEmail(email);
      if (existingUser) {
        return res.status(409).json({
          error: 'User already exists',
          message: 'A user with this email already exists'
        });
      }
      
      const existingUsername = await User.findByUsername(username);
      if (existingUsername) {
        return res.status(409).json({
          error: 'Username taken',
          message: 'This username is already taken'
        });
      }
      
      const user = await User.create({ username, email, password, full_name });
      const token = generateToken({ userId: user.id });
      
      res.status(201).json({
        message: 'User registered successfully',
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          full_name: user.full_name
        },
        token
      });
    } catch (error) {
      console.error('Registration error:', error);
      res.status(500).json({
        error: 'Registration failed',
        message: 'An error occurred during registration'
      });
    }
  }

  static async login(req, res) {
    try {
      const { email, password } = req.body;
      
      if (!email || !password) {
        return res.status(400).json({
          error: 'Validation error',
          message: 'Email and password are required'
        });
      }
      
      const user = await User.findByEmail(email);
      
      if (!user) {
        return res.status(401).json({
          error: 'Invalid credentials',
          message: 'Email or password is incorrect'
        });
      }
      
      const isValidPassword = await User.verifyPassword(password, user.password_hash);
      
      if (!isValidPassword) {
        return res.status(401).json({
          error: 'Invalid credentials',
          message: 'Email or password is incorrect'
        });
      }
      
      const token = generateToken({ userId: user.id });
      
      res.json({
        message: 'Login successful',
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          full_name: user.full_name
        },
        token
      });
    } catch (error) {
      console.error('Login error:', error);
      res.status(500).json({
        error: 'Login failed',
        message: 'An error occurred during login'
      });
    }
  }
}

module.exports = AuthController;
