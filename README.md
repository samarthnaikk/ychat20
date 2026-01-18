# YChat20

A modern real-time chat application built for seamless communication.

## Overview

YChat20 is a chat application designed to provide real-time messaging capabilities. This project aims to deliver a fast, reliable, and user-friendly communication platform.

## Tech Stack

- **Backend**: Node.js with Express.js
- **Database**: MongoDB with Mongoose
- **Authentication**: JWT (JSON Web Tokens) with bcrypt password hashing
- **Real-time Communication**: WebSocket (to be implemented)
- **Frontend**: To be determined

## Prerequisites

Before you begin, ensure you have the following installed:
- Node.js (v14 or higher)
- npm or yarn
- MongoDB (running locally or a MongoDB Atlas connection string)
- Git

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/samarthnaikk/ychat20.git
   cd ychat20
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the root directory based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
   
   Update the `.env` file with your configuration:
   ```
   PORT=3000
   MONGODB_URI=mongodb://localhost:27017/ychat20
   JWT_SECRET=your-secure-jwt-secret-key
   JWT_EXPIRES_IN=7d
   NODE_ENV=development
   ```

4. **Start MongoDB**
   
   Make sure MongoDB is running locally or update `MONGODB_URI` with your MongoDB Atlas connection string.

5. **Run the application**
   ```bash
   npm start
   ```

## Development

To run the application in development mode with hot-reload:

```bash
npm run dev
```

## Project Structure

```
ychat20/
├── src/
│   ├── config/
│   │   └── database.js       # MongoDB connection configuration
│   ├── controllers/
│   │   └── authController.js # Authentication logic
│   ├── middleware/
│   │   ├── auth.js           # JWT authentication middleware
│   │   └── validation.js     # Input validation middleware
│   ├── models/
│   │   └── User.js           # User model with password hashing
│   ├── routes/
│   │   └── authRoutes.js     # Authentication routes
│   ├── utils/
│   │   └── jwt.js            # JWT utility functions
│   └── server.js             # Main application entry point
├── .env.example              # Environment variables template
├── .gitignore
├── package.json
├── README.md
└── LICENSE
```

## API Documentation

### Authentication Endpoints

#### Register a New User
**POST** `/api/auth/register`

Register a new user with secure password hashing.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Validation Requirements:**
- Username: 3-30 characters, alphanumeric and underscores only
- Email: Valid email format
- Password: At least 6 characters, must contain uppercase, lowercase, and number

**Success Response (201):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": {
      "id": "user_id",
      "username": "johndoe",
      "email": "john@example.com",
      "createdAt": "2024-01-01T00:00:00.000Z"
    },
    "token": "jwt_token_here"
  }
}
```

**Error Responses:**
- 400: Validation errors or duplicate email/username
- 500: Server error

---

#### Login
**POST** `/api/auth/login`

Authenticate a user and receive a JWT token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "user_id",
      "username": "johndoe",
      "email": "john@example.com",
      "createdAt": "2024-01-01T00:00:00.000Z"
    },
    "token": "jwt_token_here"
  }
}
```

**Error Responses:**
- 400: Missing email or password
- 401: Invalid credentials
- 500: Server error

---

#### Get Current User
**GET** `/api/auth/me`

Get the profile of the currently authenticated user.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_id",
      "username": "johndoe",
      "email": "john@example.com",
      "createdAt": "2024-01-01T00:00:00.000Z"
    }
  }
}
```

**Error Responses:**
- 401: Not authorized or invalid token
- 500: Server error

---

### Security Features

- **Password Hashing**: All passwords are hashed using bcrypt with salt (10 rounds)
- **JWT Authentication**: Tokens expire after 7 days (configurable)
- **Protected Routes**: Authentication middleware validates JWT tokens
- **Input Validation**: All inputs are validated and sanitized
- **Secure Error Messages**: Error responses don't leak sensitive information

### Using the API

Example using cURL:

**Register:**
```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"johndoe","email":"john@example.com","password":"SecurePass123"}'
```

**Login:**
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"SecurePass123"}'
```

**Get Profile (with token):**
```bash
curl -X GET http://localhost:3000/api/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please open an issue in the GitHub repository.