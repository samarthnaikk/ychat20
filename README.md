# YChat20

A modern real-time chat application built for seamless communication.

## Overview

YChat20 is a chat application designed to provide real-time messaging capabilities. This project aims to deliver a fast, reliable, and user-friendly communication platform.

## Tech Stack

- **Backend**: Node.js / Python (to be determined based on implementation)
- **Real-time Communication**: WebSocket
- **Database**: To be determined
- **Authentication**: To be implemented
- **Frontend**: To be determined

## Prerequisites

Before you begin, ensure you have the following installed:
- Node.js (v14 or higher) OR Python (v3.8 or higher)
- npm or yarn (for Node.js) OR pip (for Python)
- Git

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/samarthnaikk/ychat20.git
   cd ychat20
   ```

2. **Install dependencies**
   
   For Node.js:
   ```bash
   npm install
   ```
   
   For Python:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the root directory and add the following variables:
   ```
   PORT=3000
   DATABASE_URL=your_database_url
   JWT_SECRET=your_jwt_secret
   ```

4. **Run the application**
   
   For Node.js:
   ```bash
   npm start
   ```
   
   For Python:
   ```bash
   python app.py
   ```

## Development

To run the application in development mode with hot-reload:

For Node.js:
```bash
npm run dev
```

For Python:
```bash
python app.py --debug
```

## Project Structure

```
ychat20/
├── README.md
├── .gitignore
├── LICENSE
└── (source files to be added)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please open an issue in the GitHub repository.