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

## Notes

- All timestamps are in ISO 8601 format
- Tokens should be stored securely on the client side (e.g., in httpOnly cookies or secure storage)
- Always use HTTPS in production to protect sensitive data in transit
- The JWT secret key should be kept secure and never exposed
- Rate limits are applied per IP address
- Database uses SQLite for development; PostgreSQL is recommended for production
