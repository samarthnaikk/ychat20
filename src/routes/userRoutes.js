const express = require('express');
const UserController = require('../controllers/userController');
const authenticate = require('../middleware/authenticate');

const router = express.Router();

router.get('/me', authenticate, UserController.getProfile);
router.put('/me', authenticate, UserController.updateProfile);

module.exports = router;
