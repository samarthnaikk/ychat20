const WebSocket = require('ws');
const { verifyToken } = require('../utils/jwt');
const Message = require('../models/Message');

class WebSocketHandler {
  constructor(server) {
    this.wss = new WebSocket.Server({ server });
    this.clients = new Map();
    this.setupWebSocketServer();
  }

  setupWebSocketServer() {
    this.wss.on('connection', (ws, req) => {
      console.log('New WebSocket connection attempt');
      
      ws.on('message', async (data) => {
        try {
          const message = JSON.parse(data);
          await this.handleMessage(ws, message);
        } catch (error) {
          console.error('WebSocket message error:', error);
          ws.send(JSON.stringify({
            type: 'error',
            message: 'Invalid message format'
          }));
        }
      });

      ws.on('close', () => {
        this.handleDisconnect(ws);
      });

      ws.on('error', (error) => {
        console.error('WebSocket error:', error);
      });
    });

    console.log('WebSocket server initialized');
  }

  async handleMessage(ws, message) {
    const { type, token, receiver_id, content } = message;

    switch (type) {
      case 'auth':
        await this.handleAuth(ws, token);
        break;

      case 'message':
        await this.handleChatMessage(ws, receiver_id, content);
        break;

      case 'ping':
        ws.send(JSON.stringify({ type: 'pong' }));
        break;

      default:
        ws.send(JSON.stringify({
          type: 'error',
          message: 'Unknown message type'
        }));
    }
  }

  async handleAuth(ws, token) {
    if (!token) {
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Authentication token required'
      }));
      return;
    }

    const decoded = verifyToken(token);

    if (!decoded) {
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Invalid or expired token'
      }));
      ws.close();
      return;
    }

    ws.userId = decoded.userId;
    this.clients.set(decoded.userId, ws);

    ws.send(JSON.stringify({
      type: 'auth_success',
      message: 'Authentication successful',
      userId: decoded.userId
    }));

    console.log(`User ${decoded.userId} authenticated via WebSocket`);
  }

  async handleChatMessage(ws, receiver_id, content) {
    if (!ws.userId) {
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Not authenticated. Please authenticate first.'
      }));
      return;
    }

    if (!receiver_id || !content) {
      ws.send(JSON.stringify({
        type: 'error',
        message: 'receiver_id and content are required'
      }));
      return;
    }

    if (ws.userId === receiver_id) {
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Cannot send message to yourself'
      }));
      return;
    }

    try {
      const savedMessage = await Message.create({
        sender_id: ws.userId,
        receiver_id: parseInt(receiver_id),
        content: content.trim()
      });

      const messagePayload = {
        type: 'message',
        message: {
          id: savedMessage.id,
          sender_id: savedMessage.sender_id,
          receiver_id: savedMessage.receiver_id,
          content: savedMessage.content,
          created_at: savedMessage.created_at
        }
      };

      ws.send(JSON.stringify({
        type: 'message_sent',
        message: messagePayload.message
      }));

      const receiverWs = this.clients.get(receiver_id);
      if (receiverWs && receiverWs.readyState === WebSocket.OPEN) {
        receiverWs.send(JSON.stringify(messagePayload));
      }

      console.log(`Message from user ${ws.userId} to ${receiver_id} delivered`);
    } catch (error) {
      console.error('Error sending message:', error);
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Failed to send message'
      }));
    }
  }

  handleDisconnect(ws) {
    if (ws.userId) {
      this.clients.delete(ws.userId);
      console.log(`User ${ws.userId} disconnected`);
    }
  }
}

module.exports = WebSocketHandler;
