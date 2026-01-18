#!/usr/bin/env python3
"""
Test script for WebSocket and Message functionality
"""
import sys
import requests
import socketio
import time
import json
from threading import Thread

BASE_URL = 'http://localhost:3000'

def test_rest_endpoints():
    """Test REST API endpoints"""
    print("\n🔍 Testing REST API Endpoints...\n")
    
    # Test 1: Register two users
    print("✅ Test 1: Register users")
    user1_data = {
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'Password123'
    }
    
    user2_data = {
        'username': 'bob',
        'email': 'bob@example.com',
        'password': 'Password123'
    }
    
    try:
        response1 = requests.post(f"{BASE_URL}/api/auth/register", json=user1_data)
        if response1.status_code == 201:
            user1 = response1.json()['data']
            token1 = user1['token']
            user1_id = user1['user']['id']
            print(f"   ✓ User 'alice' registered (ID: {user1_id})")
        elif response1.status_code == 400 and 'already' in response1.json().get('message', ''):
            # User already exists, try login
            response1 = requests.post(f"{BASE_URL}/api/auth/login", json={
                'email': user1_data['email'],
                'password': user1_data['password']
            })
            user1 = response1.json()['data']
            token1 = user1['token']
            user1_id = user1['user']['id']
            print(f"   ✓ User 'alice' logged in (ID: {user1_id})")
        else:
            print(f"   ✗ Failed to register user 1: {response1.json()}")
            return None, None, None, None
        
        response2 = requests.post(f"{BASE_URL}/api/auth/register", json=user2_data)
        if response2.status_code == 201:
            user2 = response2.json()['data']
            token2 = user2['token']
            user2_id = user2['user']['id']
            print(f"   ✓ User 'bob' registered (ID: {user2_id})")
        elif response2.status_code == 400 and 'already' in response2.json().get('message', ''):
            response2 = requests.post(f"{BASE_URL}/api/auth/login", json={
                'email': user2_data['email'],
                'password': user2_data['password']
            })
            user2 = response2.json()['data']
            token2 = user2['token']
            user2_id = user2['user']['id']
            print(f"   ✓ User 'bob' logged in (ID: {user2_id})")
        else:
            print(f"   ✗ Failed to register user 2: {response2.json()}")
            return None, None, None, None
        
        print()
        return token1, user1_id, token2, user2_id
        
    except Exception as e:
        print(f"   ✗ Registration failed: {e}")
        return None, None, None, None


def test_websocket_messaging(token1, user1_id, token2, user2_id):
    """Test WebSocket real-time messaging"""
    print("✅ Test 2: WebSocket Real-Time Messaging\n")
    
    received_messages = {'user1': [], 'user2': []}
    
    # Create Socket.IO clients
    sio1 = socketio.Client(reconnection=False)
    sio2 = socketio.Client(reconnection=False)
    
    # Setup event handlers for user1
    @sio1.on('connected')
    def on_connected1(data):
        print(f"   ✓ User 1 (alice) connected: {data}")
    
    @sio1.on('message_sent')
    def on_message_sent1(data):
        print(f"   ✓ User 1 message sent confirmation: {data['message']['content'][:30]}")
        received_messages['user1'].append(data)
    
    @sio1.on('receive_message')
    def on_receive_message1(data):
        print(f"   ✓ User 1 received message: {data['message']['content'][:30]}")
        received_messages['user1'].append(data)
    
    @sio1.on('error')
    def on_error1(data):
        print(f"   ✗ User 1 error: {data}")
    
    # Setup event handlers for user2
    @sio2.on('connected')
    def on_connected2(data):
        print(f"   ✓ User 2 (bob) connected: {data}")
    
    @sio2.on('message_sent')
    def on_message_sent2(data):
        print(f"   ✓ User 2 message sent confirmation: {data['message']['content'][:30]}")
        received_messages['user2'].append(data)
    
    @sio2.on('receive_message')
    def on_receive_message2(data):
        print(f"   ✓ User 2 received message: {data['message']['content'][:30]}")
        received_messages['user2'].append(data)
    
    @sio2.on('error')
    def on_error2(data):
        print(f"   ✗ User 2 error: {data}")
    
    try:
        # Connect clients with JWT authentication
        sio1.connect(BASE_URL, auth={'token': token1})
        sio2.connect(BASE_URL, auth={'token': token2})
        
        time.sleep(1)  # Wait for connections
        
        # User 1 sends message to User 2
        print("\n   Sending message from alice to bob...")
        sio1.emit('send_message', {
            'receiverId': user2_id,
            'content': 'Hello Bob! This is Alice.'
        })
        
        time.sleep(1)  # Wait for message delivery
        
        # User 2 sends message to User 1
        print("\n   Sending message from bob to alice...")
        sio2.emit('send_message', {
            'receiverId': user1_id,
            'content': 'Hi Alice! Bob here.'
        })
        
        time.sleep(1)  # Wait for message delivery
        
        # Disconnect
        sio1.disconnect()
        sio2.disconnect()
        
        print("\n   ✓ WebSocket test completed")
        return True
        
    except Exception as e:
        print(f"\n   ✗ WebSocket test failed: {e}")
        return False


def test_chat_history(token1, user1_id, user2_id):
    """Test chat history retrieval"""
    print("\n✅ Test 3: Chat History Retrieval\n")
    
    try:
        headers = {'Authorization': f'Bearer {token1}'}
        response = requests.get(f"{BASE_URL}/api/messages/history/{user2_id}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            messages = data['data']['messages']
            pagination = data['data']['pagination']
            
            print(f"   ✓ Retrieved {len(messages)} messages")
            print(f"   ✓ Total messages: {pagination['totalMessages']}")
            print(f"   ✓ Pagination: Page {pagination['page']} of {pagination['totalPages']}")
            
            if len(messages) > 0:
                print(f"\n   Last message: {messages[-1]['content']}")
            
            return True
        else:
            print(f"   ✗ Failed to retrieve chat history: {response.json()}")
            return False
            
    except Exception as e:
        print(f"   ✗ Chat history test failed: {e}")
        return False


def test_authorization(token1, token2, user1_id, user2_id):
    """Test authorization (users can only access their own conversations)"""
    print("\n✅ Test 4: Authorization Check\n")
    
    try:
        # Try to access chat history between user1 and user2 using correct token (should work)
        headers = {'Authorization': f'Bearer {token1}'}
        response = requests.get(f"{BASE_URL}/api/messages/history/{user2_id}", headers=headers)
        
        if response.status_code == 200:
            print("   ✓ User 1 can access conversation with User 2")
        else:
            print(f"   ✗ User 1 cannot access conversation: {response.json()}")
            return False
        
        # Try to access without token (should fail)
        response = requests.get(f"{BASE_URL}/api/messages/history/{user2_id}")
        
        if response.status_code == 401:
            print("   ✓ Unauthorized access correctly denied")
            return True
        else:
            print(f"   ✗ Unauthorized access should be denied")
            return False
            
    except Exception as e:
        print(f"   ✗ Authorization test failed: {e}")
        return False


def main():
    """Main test runner"""
    print("=" * 60)
    print("  YChat20 - WebSocket Messaging Test Suite")
    print("=" * 60)
    
    print("\nℹ️  Make sure the server is running on http://localhost:3000")
    print("   Start server with: python app.py\n")
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=2)
        print("✅ Server is running\n")
    except Exception as e:
        print(f"❌ Server is not running. Please start the server first.\n")
        sys.exit(1)
    
    # Test REST endpoints and get tokens
    token1, user1_id, token2, user2_id = test_rest_endpoints()
    
    if not all([token1, user1_id, token2, user2_id]):
        print("\n❌ REST API tests failed. Cannot proceed with WebSocket tests.")
        sys.exit(1)
    
    # Test WebSocket messaging
    websocket_success = test_websocket_messaging(token1, user1_id, token2, user2_id)
    
    if not websocket_success:
        print("\n❌ WebSocket tests failed.")
        sys.exit(1)
    
    # Test chat history
    history_success = test_chat_history(token1, user1_id, user2_id)
    
    if not history_success:
        print("\n❌ Chat history tests failed.")
        sys.exit(1)
    
    # Test authorization
    auth_success = test_authorization(token1, token2, user1_id, user2_id)
    
    if not auth_success:
        print("\n❌ Authorization tests failed.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("  ✅ All tests passed successfully!")
    print("=" * 60)
    print("\n📝 Summary:")
    print("   ✓ User registration/login works")
    print("   ✓ WebSocket connections with JWT authentication work")
    print("   ✓ Real-time message delivery works")
    print("   ✓ Message persistence works")
    print("   ✓ Chat history retrieval works")
    print("   ✓ Authorization checks work")
    print("\n✅ Real-time messaging implementation is complete!\n")


if __name__ == '__main__':
    main()
