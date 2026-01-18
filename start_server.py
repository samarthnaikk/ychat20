from app import create_app, socketio
import os

app = create_app('development')
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000, debug=False, allow_unsafe_werkzeug=True)
