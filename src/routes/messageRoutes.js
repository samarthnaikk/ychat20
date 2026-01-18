const express = require('express');
const MessageController = require('../controllers/messageController');
const authenticate = require('../middleware/authenticate');

const router = express.Router();

router.get('/:userId', authenticate, MessageController.getChatHistory);

module.exports = router;
