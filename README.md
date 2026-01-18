# YChat20 - Real-Time One-to-One Chat Backend

A secure, scalable backend system that enables real-time one-to-one messaging between authenticated users using WebSockets and REST APIs.

## Features

- **User Authentication**: Secure JWT-based authentication with password hashing
- **Real-Time Messaging**: WebSocket-based instant message delivery
- **Message Persistence**: All messages stored in PostgreSQL database
- **Chat History**: Paginated REST API to retrieve conversation history
- **User Profiles**: Profile management with update capabilities
- **Secure**: Authentication middleware, password hashing, and proper authorization

## Tech Stack

- **Backend Framework**: Node.js with Express.js
- **Real-Time Communication**: WebSocket (ws library)
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Password Security**: bcryptjs for hashing and salting

## Prerequisites

- Node.js (v14 or higher)
- PostgreSQL (v12 or higher)
- npm or yarn package manager

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/samarthnaikk/ychat20.git
cd ychat20
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory (use `.env.example` as template):

```env
# Server Configuration
PORT=3000
NODE_ENV=development

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ychat
DB_USER=postgres
DB_PASSWORD=your_password

# JWT Configuration
JWT_SECRET=your_secret_key_here_change_in_production
JWT_EXPIRES_IN=7d

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 4. Set Up PostgreSQL Database

Create a PostgreSQL database:

```bash
psql -U postgres
CREATE DATABASE ychat;
\q
```

### 5. Initialize Database Schema

```bash
npm run init-db
```

### 6. Start the Server

```bash
npm start
```

The server will start on `http://localhost:3000` (or the port specified in `.env`).

## API Documentation

### Base URL

```
http://localhost:3000/api
```

### Authentication Endpoints

#### Register User

**POST** `/api/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Login User

**POST** `/api/auth/login`

Login with existing credentials.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### User Profile Endpoints

All user endpoints require authentication via Bearer token in the Authorization header.

#### Get User Profile

**GET** `/api/users/me`

Get the authenticated user's profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "bio": "Software Developer",
    "created_at": "2024-01-18T10:00:00.000Z",
    "updated_at": "2024-01-18T10:00:00.000Z"
  }
}
```

#### Update User Profile

**PUT** `/api/users/me`

Update the authenticated user's profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "full_name": "John Smith",
  "bio": "Full-stack Developer"
}
```

**Response (200 OK):**
```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Smith",
    "bio": "Full-stack Developer",
    "updated_at": "2024-01-18T11:00:00.000Z"
  }
}
```

### Message Endpoints

#### Get Chat History

**GET** `/api/messages/:userId`

Get paginated chat history with a specific user.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit` (optional): Number of messages to retrieve (default: 50)
- `offset` (optional): Number of messages to skip (default: 0)

**Example:**
```
GET /api/messages/2?limit=20&offset=0
```

**Response (200 OK):**
```json
{
  "messages": [
    {
      "id": 1,
      "sender_id": 1,
      "receiver_id": 2,
      "content": "Hello!",
      "created_at": "2024-01-18T10:30:00.000Z",
      "read_at": null,
      "sender_username": "johndoe"
    },
    {
      "id": 2,
      "sender_id": 2,
      "receiver_id": 1,
      "content": "Hi there!",
      "created_at": "2024-01-18T10:31:00.000Z",
      "read_at": "2024-01-18T10:31:30.000Z",
      "sender_username": "janedoe"
    }
  ],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 2
  }
}
```

## WebSocket Documentation

### Connection

Connect to the WebSocket server at:

```
ws://localhost:3000
```

### Authentication

Before sending messages, you must authenticate using your JWT token:

**Send:**
```json
{
  "type": "auth",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Receive:**
```json
{
  "type": "auth_success",
  "message": "Authentication successful",
  "userId": 1
}
```

### Sending Messages

After authentication, send messages using:

**Send:**
```json
{
  "type": "message",
  "receiver_id": 2,
  "content": "Hello, how are you?"
}
```

**Receive (sender confirmation):**
```json
{
  "type": "message_sent",
  "message": {
    "id": 123,
    "sender_id": 1,
    "receiver_id": 2,
    "content": "Hello, how are you?",
    "created_at": "2024-01-18T10:30:00.000Z"
  }
}
```

### Receiving Messages

When someone sends you a message:

**Receive:**
```json
{
  "type": "message",
  "message": {
    "id": 124,
    "sender_id": 2,
    "receiver_id": 1,
    "content": "I'm doing great, thanks!",
    "created_at": "2024-01-18T10:31:00.000Z"
  }
}
```

### Keep-Alive (Ping/Pong)

To keep the connection alive:

**Send:**
```json
{
  "type": "ping"
}
```

**Receive:**
```json
{
  "type": "pong"
}
```

### Error Messages

Errors are sent in the following format:

```json
{
  "type": "error",
  "message": "Error description"
}
```

## Project Structure

```
ychat20/
├── database/
│   ├── init.js           # Database initialization script
│   └── schema.sql        # Database schema definition
├── src/
│   ├── config/
│   │   └── database.js   # Database connection configuration
│   ├── controllers/
│   │   ├── authController.js    # Authentication logic
│   │   ├── messageController.js # Message handling logic
│   │   └── userController.js    # User profile logic
│   ├── middleware/
│   │   └── authenticate.js      # JWT authentication middleware
│   ├── models/
│   │   ├── Message.js    # Message data model
│   │   └── User.js       # User data model
│   ├── routes/
│   │   ├── authRoutes.js    # Authentication routes
│   │   ├── messageRoutes.js # Message routes
│   │   └── userRoutes.js    # User routes
│   ├── utils/
│   │   └── jwt.js        # JWT utility functions
│   ├── websocket/
│   │   └── WebSocketHandler.js  # WebSocket server logic
│   └── server.js         # Main server entry point
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── package.json          # Project dependencies
└── README.md             # This file
```

## Error Handling

All API endpoints return errors in a consistent format:

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

Common HTTP status codes:
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or failed
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `500 Internal Server Error`: Server error

## Security Features

- **Password Hashing**: All passwords are hashed using bcrypt with salt rounds
- **JWT Authentication**: Secure token-based authentication
- **Authorization**: Users can only access their own profile data
- **Input Validation**: All inputs are validated before processing
- **SQL Injection Protection**: Parameterized queries prevent SQL injection
- **CORS Configuration**: Configurable CORS for frontend integration

## Development

### Running in Development Mode

```bash
npm run dev
```

### Database Management

To reset the database:

```bash
# Drop and recreate the database
psql -U postgres
DROP DATABASE ychat;
CREATE DATABASE ychat;
\q

# Reinitialize schema
npm run init-db
```

## Testing the Application

### Using cURL

**Register a user:**
```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Get profile:**
```bash
curl -X GET http://localhost:3000/api/users/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using WebSocket Client

You can test WebSocket functionality using tools like:
- [websocat](https://github.com/vi/websocat) (command-line)
- [Postman](https://www.postman.com/) (GUI)
- Browser console with JavaScript WebSocket API

## License

ISC

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.