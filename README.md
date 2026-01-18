# YChat20

A modern real-time chat application built for seamless communication.

## Overview

YChat20 is a chat application designed to provide real-time messaging capabilities. This project aims to deliver a fast, reliable, and user-friendly communication platform.

## Tech Stack

- **Backend**: Python with Flask
- **Database**: SQLite (development) / PostgreSQL (production recommended)
- **Authentication**: JWT (JSON Web Tokens) with bcrypt password hashing
- **Real-time Communication**: WebSocket (to be implemented)
- **Frontend**: HTML/CSS (to be implemented)

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package manager)
- Git

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/samarthnaikk/ychat20.git
   cd ychat20
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the root directory based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
   
   Update the `.env` file with your configuration:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   PORT=3000
   DATABASE_URL=sqlite:///ychat20.db
   JWT_SECRET_KEY=your-secure-jwt-secret-key
   JWT_ACCESS_TOKEN_EXPIRES=604800
   CORS_ORIGINS=*
   ```

5. **Run the application**
   ```bash
   python app.py
   ```
   
   The server will start on http://localhost:3000

## Development

To run the application in development mode:

```bash
export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
python app.py
```

## Project Structure

```
ychat20/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config/
│   │   └── settings.py          # Configuration classes
│   ├── models/
│   │   └── user.py              # User model with password hashing
│   ├── routes/
│   │   └── auth_routes.py       # Authentication endpoints
│   ├── middleware/
│   │   └── auth.py              # JWT authentication decorator
│   └── utils/
│       └── validation.py        # Input validation utilities
├── app.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── validate.py                  # Validation script
├── .env.example                 # Environment variables template
├── .gitignore
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
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "createdAt": "2024-01-01T00:00:00"
    },
    "token": "******"
  }
}
```

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
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "createdAt": "2024-01-01T00:00:00"
    },
    "token": "******"
  }
}
```

---

#### Get Current User
**GET** `/api/auth/me`

Get the profile of the currently authenticated user.

**Headers:**
```
Authorization: ******
```

**Success Response (200):**
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

---

### Security Features

- **Password Hashing**: All passwords are hashed using bcrypt
- **JWT Authentication**: Tokens expire after 7 days (configurable)
- **Protected Routes**: Authentication decorator validates JWT tokens
- **Input Validation**: All inputs are validated and sanitized
- **Rate Limiting**: 5 req/15min for auth, 100 req/15min for general endpoints
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
  -H "Authorization: ******"
```

## Testing

Run the validation script to verify the implementation:

```bash
python validate.py
```

This will test:
- Password hashing functionality
- JWT token generation and verification
- Module loading and structure
- Security feature implementation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please open an issue in the GitHub repository.
