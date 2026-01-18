const express = require('express');
const http = require('http');
const cors = require('cors');
require('dotenv').config();

const authRoutes = require('./routes/authRoutes');
const userRoutes = require('./routes/userRoutes');
const messageRoutes = require('./routes/messageRoutes');
const WebSocketHandler = require('./websocket/WebSocketHandler');

const app = express();
const server = http.createServer(app);

const PORT = process.env.PORT || 3000;
const allowedOrigins = process.env.ALLOWED_ORIGINS
  ? process.env.ALLOWED_ORIGINS.split(',')
  : ['http://localhost:3000', 'http://localhost:3001'];

app.use(cors({
  origin: allowedOrigins,
  credentials: true
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

app.get('/', (req, res) => {
  res.json({
    message: 'YChat20 API Server',
    version: '1.0.0',
    endpoints: {
      auth: '/api/auth',
      users: '/api/users',
      messages: '/api/messages'
    }
  });
});

app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);
app.use('/api/messages', messageRoutes);

app.use((req, res) => {
  res.status(404).json({
    error: 'Not found',
    message: 'The requested endpoint does not exist'
  });
});

app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({
    error: 'Internal server error',
    message: 'An unexpected error occurred'
  });
});

new WebSocketHandler(server);

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`HTTP API: http://localhost:${PORT}`);
  console.log(`WebSocket: ws://localhost:${PORT}`);
});

module.exports = app;
