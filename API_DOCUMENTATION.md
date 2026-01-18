# API Documentation

## Authentication API

YChat20 uses JWT (JSON Web Tokens) for authentication. All authentication endpoints are rate-limited to prevent abuse.

### Base URL
```
http://localhost:3000/api/auth
```

---

## Endpoints

### 1. Register New User

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

**Validation Rules:**
- `username`: 3-30 characters, alphanumeric and underscores only
- `email`: Valid email format
- `password`: Minimum 6 characters, must contain at least one uppercase letter, one lowercase letter, and one number

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": {
      "id": "507f1f77bcf86cd799439011",
      "username": "johndoe",
      "email": "john@example.com",
      "createdAt": "2024-01-18T10:00:00.000Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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
    {
      "field": "password",
      "message": "Password must contain at least one uppercase letter, one lowercase letter, and one number"
    }
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
  "message": "Too many authentication attempts, please try again after 15 minutes"
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
      "id": "507f1f77bcf86cd799439011",
      "username": "johndoe",
      "email": "john@example.com",
      "createdAt": "2024-01-18T10:00:00.000Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error Responses:**

*400 Bad Request - Missing Credentials:*
```json
{
  "success": false,
  "message": "Please provide email and password"
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
  "message": "Too many authentication attempts, please try again after 15 minutes"
}
```

---

### 3. Get Current User

Get the profile information of the currently authenticated user.

**Endpoint:** `GET /api/auth/me`

**Rate Limit:** 100 requests per 15 minutes per IP

**Request Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "507f1f77bcf86cd799439011",
      "username": "johndoe",
      "email": "john@example.com",
      "createdAt": "2024-01-18T10:00:00.000Z"
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

## Authentication Flow

### Registration Flow
1. Client sends registration request with username, email, and password
2. Server validates input according to validation rules
3. Server checks for duplicate email/username
4. Server hashes password using bcrypt (10 salt rounds)
5. Server creates user in database
6. Server generates JWT token (expires in 7 days by default)
7. Server returns user info and token

### Login Flow
1. Client sends login request with email and password
2. Server validates input
3. Server finds user by email
4. Server compares provided password with stored hash using bcrypt
5. Server generates JWT token if password matches
6. Server returns user info and token

### Protected Route Access Flow
1. Client includes JWT token in Authorization header
2. Server validates Bearer token format
3. Server verifies JWT signature and expiration
4. Server finds user associated with token
5. Server attaches user to request and proceeds
6. Server returns requested data

---

## Security Features

### Password Security
- Passwords are hashed using bcryptjs with 10 salt rounds
- Passwords are never stored or transmitted in plain text
- Password comparison is done securely using bcrypt.compare()
- Passwords are excluded from JSON responses automatically

### Token Security
- JWT tokens are signed with a secret key (must be set in production)
- Tokens expire after 7 days (configurable via JWT_EXPIRES_IN)
- Tokens are validated on every protected route access
- Invalid or expired tokens are rejected

### Rate Limiting
- Authentication endpoints (register/login): 5 requests per 15 minutes per IP
- General endpoints: 100 requests per 15 minutes per IP
- Prevents brute force attacks and API abuse

### Input Validation
- All inputs are validated using express-validator
- Email addresses are normalized (lowercase, trimmed)
- Usernames are sanitized (alphanumeric and underscores only)
- Password strength requirements enforced

### Error Handling
- Error messages don't leak sensitive information
- Generic "Invalid credentials" message for failed logins
- Validation errors provide helpful feedback without exposing system details

---

## Example Usage

### Using cURL

**Register:**
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

**Get Current User:**
```bash
curl -X GET http://localhost:3000/api/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### Using JavaScript (Fetch API)

**Register:**
```javascript
const response = await fetch('http://localhost:3000/api/auth/register', {
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

const data = await response.json();
console.log(data);
```

**Login:**
```javascript
const response = await fetch('http://localhost:3000/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'john@example.com',
    password: 'SecurePass123'
  })
});

const data = await response.json();
const token = data.data.token;

// Store token for future requests
localStorage.setItem('token', token);
```

**Get Current User:**
```javascript
const token = localStorage.getItem('token');

const response = await fetch('http://localhost:3000/api/auth/me', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const data = await response.json();
console.log(data);
```

---

## Environment Variables

The following environment variables should be configured in your `.env` file:

```env
# Server Configuration
PORT=3000

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/ychat20

# JWT Configuration (REQUIRED in production)
JWT_SECRET=your-secure-random-secret-key
JWT_EXPIRES_IN=7d

# Environment
NODE_ENV=development
```

**Important:** 
- `JWT_SECRET` must be set to a strong, random value in production
- The application will throw an error if `JWT_SECRET` is not set in production mode
- Never commit your `.env` file to version control

---

## Testing the API

A validation script is included to verify the implementation:

```bash
cd src
node validate.js
```

This will test:
- Password hashing functionality
- JWT token generation and verification
- Module loading and structure
- Security feature implementation

---

## Error Codes

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

## Next Steps

This authentication system provides the foundation for:
- Real-time messaging features
- User profiles and settings
- WebSocket authentication
- Friend requests and contacts
- Chat rooms and group messaging
