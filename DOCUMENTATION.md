# API Documentation

YChat20 API documentation for all available endpoints.

## Base URL

```
http://localhost:3000
```

---

## Authentication Endpoints

All authentication endpoints are under `/api/auth`.

### 1. Register a New User

Create a new user account with secure password hashing.

**Endpoint:** `POST /api/auth/register`

**Rate Limit:** 5 requests per 15 minutes per IP

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Validation Requirements:**
- **Username**: 3-30 characters, alphanumeric and underscores only
- **Email**: Valid email format (normalized to lowercase)
- **Password**: Minimum 6 characters, must contain at least one uppercase letter, one lowercase letter, and one number

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "createdAt": "2024-01-01T00:00:00"
    },
    "token": "******"
  }
}
```

**Error Responses:**

*400 Bad Request - Validation Error:*
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    "Password must contain at least one uppercase letter"
  ]
}
```

*400 Bad Request - Duplicate Email:*
```json
{
  "success": false,
  "message": "Email already registered"
}
```

*400 Bad Request - Duplicate Username:*
```json
{
  "success": false,
  "message": "Username already taken"
}
```

*429 Too Many Requests:*
```json
{
  "success": false,
  "message": "5 per 15 minutes"
}
```

---

### 2. Login

Authenticate an existing user and receive a JWT token.

**Endpoint:** `POST /api/auth/login`

**Rate Limit:** 5 requests per 15 minutes per IP

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "createdAt": "2024-01-01T00:00:00"
    },
    "token": "******"
  }
}
```

**Error Responses:**

*400 Bad Request - Missing Credentials:*
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    "Email is required",
    "Password is required"
  ]
}
```

*401 Unauthorized - Invalid Credentials:*
```json
{
  "success": false,
  "message": "Invalid credentials"
}
```

*429 Too Many Requests:*
```json
{
  "success": false,
  "message": "5 per 15 minutes"
}
```

---

### 3. Get Current User

Retrieve the profile information of the currently authenticated user.

**Endpoint:** `GET /api/auth/me`

**Rate Limit:** 100 requests per 15 minutes per IP

**Request Headers:**
```
Authorization: ******
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "createdAt": "2024-01-01T00:00:00"
    }
  }
}
```

**Error Responses:**

*401 Unauthorized - Missing Token:*
```json
{
  "success": false,
  "message": "Not authorized to access this route"
}
```

*401 Unauthorized - Invalid Token:*
```json
{
  "success": false,
  "message": "Not authorized to access this route"
}
```

*401 Unauthorized - User Not Found:*
```json
{
  "success": false,
  "message": "User not found"
}
```

---

## Root Endpoint

### Get API Information

Get basic information about the API.

**Endpoint:** `GET /`

**Request Headers:** None required

**Success Response (200 OK):**
```json
{
  "message": "YChat20 API",
  "version": "1.0.0",
  "endpoints": {
    "register": "POST /api/auth/register",
    "login": "POST /api/auth/login",
    "me": "GET /api/auth/me (Protected)"
  }
}
```

---

## Security Features

### Password Security
- Passwords are hashed using **bcrypt** algorithm
- Passwords are never stored or transmitted in plain text
- Password comparison is done securely using bcrypt's built-in comparison
- Passwords are automatically excluded from JSON responses

### JWT Token Security
- JWT tokens are signed with a secret key (configurable via environment)
- Tokens expire after **7 days** by default (configurable via `JWT_ACCESS_TOKEN_EXPIRES`)
- Tokens must be included in the `Authorization` header as `******`
- Invalid or expired tokens are rejected with 401 status

### Rate Limiting
- **Authentication endpoints** (register, login): 5 requests per 15 minutes per IP address
- **General endpoints** (protected routes): 100 requests per 15 minutes per IP address
- Rate limit headers are included in responses
- Prevents brute force attacks and API abuse

### Input Validation
- All inputs are validated before processing
- Email addresses are normalized (lowercase, trimmed)
- Usernames are sanitized (alphanumeric and underscores only)
- Password strength requirements are enforced
- Validation errors return clear, actionable feedback

### Error Handling
- Error messages don't leak sensitive information
- Generic "Invalid credentials" message for failed logins
- Consistent error response format across all endpoints
- Appropriate HTTP status codes for all scenarios

---

## HTTP Status Codes

| Status Code | Meaning |
|-------------|---------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid input or validation error |
| 401 | Unauthorized - Authentication required or failed |
| 404 | Not Found - Route not found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error occurred |

---

## Example Usage

### Using cURL

**Register a new user:**
```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

**Get current user profile:**
```bash
# Replace YOUR_JWT_TOKEN with the token received from login/register
curl -X GET http://localhost:3000/api/auth/me \
  -H "Authorization: ******"
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:3000"

# Register
response = requests.post(
    f"{BASE_URL}/api/auth/register",
    json={
        "username": "johndoe",
        "email": "john@example.com",
        "password": "SecurePass123"
    }
)
data = response.json()
token = data['data']['token']

# Login
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={
        "email": "john@example.com",
        "password": "SecurePass123"
    }
)
data = response.json()
token = data['data']['token']

# Get current user
headers = {"Authorization": f"******"}
response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
user = response.json()
```

### Using JavaScript Fetch

```javascript
const BASE_URL = 'http://localhost:3000';

// Register
const registerResponse = await fetch(`${BASE_URL}/api/auth/register`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'johndoe',
    email: 'john@example.com',
    password: 'SecurePass123'
  })
});
const registerData = await registerResponse.json();
const token = registerData.data.token;

// Login
const loginResponse = await fetch(`${BASE_URL}/api/auth/login`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'john@example.com',
    password: 'SecurePass123'
  })
});
const loginData = await loginResponse.json();

// Get current user
const meResponse = await fetch(`${BASE_URL}/api/auth/me`, {
  method: 'GET',
  headers: {
    'Authorization': `******
  }
});
const userData = await meResponse.json();
console.log(userData);
```

---

## Authentication Flow

### Registration Flow
1. Client sends registration request with username, email, and password
2. Server validates input according to validation rules
3. Server checks for duplicate email/username in database
4. Server hashes password using bcrypt
5. Server creates user record in database
6. Server generates JWT token with user ID
7. Server returns user info and token to client

### Login Flow
1. Client sends login request with email and password
2. Server validates input (email and password present)
3. Server finds user by email in database
4. Server compares provided password with stored hash using bcrypt
5. If password matches, server generates JWT token
6. Server returns user info and token to client

### Protected Route Access Flow
1. Client includes JWT token in Authorization header (`******`)
2. Server extracts and verifies JWT token
3. Server decodes token to get user ID
4. Server finds user in database by ID
5. If user exists and token is valid, request proceeds
6. Server returns requested data

---

## WebSocket Real-Time Messaging

YChat20 supports real-time one-to-one messaging using WebSocket connections via Socket.IO.

### Connection

**Endpoint:** WebSocket connection to the server base URL

**Authentication:** JWT token must be provided during connection

**Connection Example (JavaScript):**
```javascript
import io from 'socket.io-client';

const token = 'your-jwt-token-here';

const socket = io('http://localhost:3000', {
  auth: {
    token: token
  }
});
```

**Connection Example (Python):**
```python
import socketio

sio = socketio.Client()
token = 'your-jwt-token-here'

sio.connect('http://localhost:3000', auth={'token': token})
```

---

### WebSocket Events

#### Client to Server Events

##### 1. send_message

Send a message to another user.

**Event:** `send_message`

**Payload:**
```json
{
  "receiverId": 2,
  "content": "Hello! How are you?"
}
```

**Validation:**
- `receiverId`: Required, must be a valid user ID
- `content`: Required, string, 1-5000 characters

**Error Response:**
```json
{
  "success": false,
  "message": "Error description"
}
```

---

#### Server to Client Events

##### 1. connected

Emitted when a client successfully connects.

**Event:** `connected`

**Payload:**
```json
{
  "success": true,
  "message": "Connected to chat server",
  "userId": 1
}
```

##### 2. message_sent

Confirmation that your message was sent and saved.

**Event:** `message_sent`

**Payload:**
```json
{
  "success": true,
  "message": {
    "id": 123,
    "senderId": 1,
    "receiverId": 2,
    "content": "Hello! How are you?",
    "timestamp": "2024-01-01T12:00:00.000000"
  }
}
```

##### 3. receive_message

Receive a message from another user (real-time delivery).

**Event:** `receive_message`

**Payload:**
```json
{
  "success": true,
  "message": {
    "id": 123,
    "senderId": 2,
    "receiverId": 1,
    "content": "I'm doing great, thanks!",
    "timestamp": "2024-01-01T12:00:05.000000"
  }
}
```

##### 4. error

Error notification for failed operations.

**Event:** `error`

**Payload:**
```json
{
  "success": false,
  "message": "Error description"
}
```

---

### WebSocket Example Implementation

**Complete JavaScript Example:**
```javascript
import io from 'socket.io-client';

// Get JWT token from login/register
const token = localStorage.getItem('token');

// Connect to server
const socket = io('http://localhost:3000', {
  auth: { token: token }
});

// Connection successful
socket.on('connected', (data) => {
  console.log('Connected:', data.message);
  console.log('Your user ID:', data.userId);
});

// Send a message
function sendMessage(receiverId, content) {
  socket.emit('send_message', {
    receiverId: receiverId,
    content: content
  });
}

// Message sent confirmation
socket.on('message_sent', (data) => {
  console.log('Message sent:', data.message);
  // Update UI to show message was sent
});

// Receive incoming messages
socket.on('receive_message', (data) => {
  console.log('New message:', data.message);
  // Display message in chat UI
});

// Handle errors
socket.on('error', (data) => {
  console.error('Error:', data.message);
});

// Example: Send a message
sendMessage(2, 'Hello there!');
```

**Complete Python Example:**
```python
import socketio

# Create client
sio = socketio.Client()

# Get JWT token
token = 'your-jwt-token'

# Event handlers
@sio.on('connected')
def on_connected(data):
    print(f"Connected: {data['message']}")
    print(f"User ID: {data['userId']}")

@sio.on('message_sent')
def on_message_sent(data):
    print(f"Message sent: {data['message']}")

@sio.on('receive_message')
def on_receive_message(data):
    print(f"New message: {data['message']}")

@sio.on('error')
def on_error(data):
    print(f"Error: {data['message']}")

# Connect with authentication
sio.connect('http://localhost:3000', auth={'token': token})

# Send a message
sio.emit('send_message', {
    'receiverId': 2,
    'content': 'Hello there!'
})

# Keep connection alive
sio.wait()
```

---

## Message History Endpoints

### 1. Get Chat History

Retrieve message history between the current user and another user.

**Endpoint:** `GET /api/messages/history/:userId`

**Rate Limit:** 100 requests per 15 minutes per IP

**Authentication:** Required (JWT token in Authorization header)

**URL Parameters:**
- `userId`: The ID of the other user in the conversation

**Query Parameters:**
- `page`: Page number (optional, default: 1, min: 1)
- `per_page`: Results per page (optional, default: 50, max: 100, min: 1)

**Request Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": 1,
        "senderId": 1,
        "receiverId": 2,
        "content": "Hello! How are you?",
        "timestamp": "2024-01-01T12:00:00.000000"
      },
      {
        "id": 2,
        "senderId": 2,
        "receiverId": 1,
        "content": "I'm doing great, thanks!",
        "timestamp": "2024-01-01T12:00:05.000000"
      }
    ],
    "pagination": {
      "page": 1,
      "perPage": 50,
      "totalPages": 1,
      "totalMessages": 2,
      "hasNext": false,
      "hasPrev": false
    }
  }
}
```

**Error Responses:**

*400 Bad Request - Invalid pagination:*
```json
{
  "success": false,
  "message": "Invalid pagination parameters"
}
```

*401 Unauthorized - No token or invalid token:*
```json
{
  "success": false,
  "message": "Not authorized to access this route"
}
```

*404 Not Found - User doesn't exist:*
```json
{
  "success": false,
  "message": "User not found"
}
```

**Example Usage:**

Using cURL:
```bash
curl -X GET http://localhost:3000/api/messages/history/2 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

With pagination:
```bash
curl -X GET "http://localhost:3000/api/messages/history/2?page=1&per_page=20" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Using JavaScript Fetch:
```javascript
const userId = 2;
const token = localStorage.getItem('token');

const response = await fetch(`http://localhost:3000/api/messages/history/${userId}?page=1&per_page=50`, {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const data = await response.json();
console.log(data.data.messages);
```

---

## Real-Time Messaging Features

### Message Delivery

- **Online Users**: Messages are delivered instantly via WebSocket when both users are connected
- **Offline Users**: Messages are saved to the database and can be retrieved via chat history API
- **Message Persistence**: All messages are permanently stored regardless of delivery status
- **Acknowledgments**: Senders receive confirmation when messages are sent

### Security

- **WebSocket Authentication**: JWT tokens required for WebSocket connections
- **Authorization**: Users can only access conversations they are part of
- **Content Validation**: Messages are validated for length and content type
- **Rate Limiting**: API endpoints are rate-limited to prevent abuse

### Limitations

- **One-to-One Only**: Group chats are not supported
- **No Message Editing**: Sent messages cannot be edited
- **No Message Deletion**: Sent messages cannot be deleted
- **No Read Receipts**: Read status is not tracked
- **No Typing Indicators**: Typing status is not supported

---

## Notes

- All timestamps are in ISO 8601 format
- Tokens should be stored securely on the client side (e.g., in httpOnly cookies or secure storage)
- Always use HTTPS in production to protect sensitive data in transit
- The JWT secret key should be kept secure and never exposed
- Rate limits are applied per IP address
- Database uses SQLite for development; PostgreSQL is recommended for production
- WebSocket connections automatically handle reconnection on disconnect
- Messages are ordered by timestamp in ascending order (oldest first)

### Production Deployment Considerations

**Scalability:**
- The current implementation uses an in-memory dictionary for active WebSocket connections
- For production deployments with multiple server instances, implement a shared storage solution like Redis for connection management
- Consider using a message queue (e.g., RabbitMQ, Redis Pub/Sub) for inter-server communication

**Storage Backend:**
- Configure a persistent storage backend for rate limiting (e.g., Redis, Memcached)
- The in-memory storage is not recommended for production use

**Server Configuration:**
- Use a production WSGI server (e.g., Gunicorn with eventlet/gevent workers) instead of Flask's development server
- Configure proper logging levels and log aggregation
- Set up monitoring and alerting for WebSocket connections and message delivery

**Example Production Configuration:**
```bash
# Install production server
pip install gunicorn eventlet

# Run with Gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:3000 app:app
```
