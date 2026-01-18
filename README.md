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
│   ├── __init__.py              # Flask app factory with SocketIO
│   ├── config/
│   │   └── settings.py          # Configuration classes
│   ├── models/
│   │   ├── user.py              # User model with password hashing
│   │   └── message.py           # Message model for chat persistence
│   ├── routes/
│   │   ├── auth_routes.py       # Authentication endpoints
│   │   └── message_routes.py    # Message history endpoints
│   ├── middleware/
│   │   └── auth.py              # JWT authentication decorator
│   ├── websocket/
│   │   └── handlers.py          # WebSocket event handlers
│   └── utils/
│       └── validation.py        # Input validation utilities
├── app.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── test_messaging.py            # WebSocket and messaging tests
├── validate.py                  # Validation script
├── .env.example                 # Environment variables template
├── .gitignore
├── README.md
└── LICENSE
```

## API Documentation

For detailed API documentation including all endpoints, request/response formats, examples, and security features, see [DOCUMENTATION.md](DOCUMENTATION.md).

### Quick Reference

**Available Endpoints:**
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Authenticate and get JWT token
- `GET /api/auth/me` - Get current user profile (requires authentication)
- `GET /api/messages/history/:userId` - Get chat history with another user (requires authentication)

**WebSocket Events:**
- `connect` - Establish WebSocket connection with JWT authentication
- `send_message` - Send a real-time message to another user
- `receive_message` - Receive real-time messages from other users
- `message_sent` - Confirmation of message delivery

**Security Features:**
- bcrypt password hashing
- JWT token authentication (7-day expiration)
- WebSocket authentication with JWT
- Rate limiting (5 req/15min for auth, 100 req/15min for general)
- Input validation and sanitization
- Protected routes with authentication decorator
- Authorization checks for message access

## Testing

### Run Validation Script

Run the validation script to verify the authentication implementation:

```bash
python validate.py
```

This will test:
- Password hashing functionality
- JWT token generation and verification
- Module loading and structure
- Security feature implementation

### Run Messaging Tests

Run the comprehensive test suite for WebSocket and messaging functionality:

```bash
# Make sure the server is running first
python app.py

# In another terminal
python test_messaging.py
```

This will test:
- User registration and authentication
- WebSocket connection with JWT authentication
- Real-time message delivery between users
- Message persistence in database
- Chat history retrieval with pagination
- Authorization checks for message access

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please open an issue in the GitHub repository.
