#!/bin/bash

# YChat20 Test Suite
# Comprehensive tests for all API endpoints and functionality

# Note: We don't use 'set -e' because we want to handle test failures gracefully

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="${BASE_URL:-http://localhost:3000}"
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test results array
declare -a FAILED_TEST_NAMES=()

# Helper functions
print_test() {
    echo -e "\n${YELLOW}TEST:${NC} $1"
    ((TOTAL_TESTS++))
}

print_pass() {
    echo -e "${GREEN}✓ PASS:${NC} $1"
    ((PASSED_TESTS++))
}

print_fail() {
    echo -e "${RED}✗ FAIL:${NC} $1"
    ((FAILED_TESTS++))
    FAILED_TEST_NAMES+=("$1")
}

print_info() {
    echo -e "${YELLOW}INFO:${NC} $1"
}

# Check if server is running
check_server() {
    print_info "Checking if server is running at $BASE_URL..."
    if ! curl -s -f "$BASE_URL" > /dev/null 2>&1; then
        echo -e "${RED}ERROR:${NC} Server is not running at $BASE_URL"
        echo "Please start the server with: python app.py"
        exit 1
    fi
    print_info "Server is running"
}

# Generate random string for unique test data
random_string() {
    echo "test_$(date +%s)_$RANDOM"
}

# Test 1: User Registration
test_registration() {
    print_test "User Registration"
    
    local username=$(random_string)
    local email="${username}@example.com"
    local password="TestPass123"
    
    local response=$(curl -s -X POST "$BASE_URL/api/auth/register" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$username\",\"email\":\"$email\",\"password\":\"$password\"}")
    
    if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
        TOKEN1=$(echo "$response" | jq -r '.data.token')
        USER1_ID=$(echo "$response" | jq -r '.data.user.id')
        print_pass "User registration successful (ID: $USER1_ID)"
        export TOKEN1 USER1_ID
    else
        print_fail "User registration failed: $response"
    fi
}

# Test 2: User Login
test_login() {
    print_test "User Login"
    
    # Create a new user first
    local username=$(random_string)
    local email="${username}@example.com"
    local password="TestPass123"
    
    curl -s -X POST "$BASE_URL/api/auth/register" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$username\",\"email\":\"$email\",\"password\":\"$password\"}" > /dev/null
    
    # Now login
    local response=$(curl -s -X POST "$BASE_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$email\",\"password\":\"$password\"}")
    
    if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
        print_pass "User login successful"
    else
        print_fail "User login failed: $response"
    fi
}

# Test 3: Get Current User Profile
test_get_profile() {
    print_test "Get Current User Profile"
    
    if [ -z "$TOKEN1" ]; then
        print_fail "No token available (depends on registration test)"
        return
    fi
    
    local response=$(curl -s -X GET "$BASE_URL/api/auth/me" \
        -H "Authorization: Bearer $TOKEN1")
    
    if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
        print_pass "Get profile successful"
    else
        print_fail "Get profile failed: $response"
    fi
}

# Test 4: Invalid Login
test_invalid_login() {
    print_test "Invalid Login (Wrong Password)"
    
    local response=$(curl -s -X POST "$BASE_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"nonexistent@example.com","password":"WrongPass123"}')
    
    if echo "$response" | jq -e '.success == false' > /dev/null 2>&1; then
        print_pass "Invalid login correctly rejected"
    else
        print_fail "Invalid login should be rejected"
    fi
}

# Test 5: Unauthorized Access
test_unauthorized_access() {
    print_test "Unauthorized Access to Protected Route"
    
    local response=$(curl -s -X GET "$BASE_URL/api/auth/me")
    
    if echo "$response" | jq -e '.success == false' > /dev/null 2>&1; then
        print_pass "Unauthorized access correctly denied"
    else
        print_fail "Unauthorized access should be denied"
    fi
}

# Test 6: Chat History - Create Two Users and Send Messages
test_chat_history() {
    print_test "Chat History Retrieval"
    
    # Create two users
    local user1=$(random_string)
    local user2=$(random_string)
    
    local resp1=$(curl -s -X POST "$BASE_URL/api/auth/register" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$user1\",\"email\":\"${user1}@example.com\",\"password\":\"TestPass123\"}")
    
    local resp2=$(curl -s -X POST "$BASE_URL/api/auth/register" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$user2\",\"email\":\"${user2}@example.com\",\"password\":\"TestPass123\"}")
    
    local token1=$(echo "$resp1" | jq -r '.data.token')
    local user1_id=$(echo "$resp1" | jq -r '.data.user.id')
    local user2_id=$(echo "$resp2" | jq -r '.data.user.id')
    
    # Try to get chat history (should be empty)
    local response=$(curl -s -X GET "$BASE_URL/api/messages/history/$user2_id" \
        -H "Authorization: Bearer $token1")
    
    if echo "$response" | jq -e '.success == true' > /dev/null 2>&1; then
        print_pass "Chat history retrieval successful"
    else
        print_fail "Chat history retrieval failed: $response"
    fi
}

# Test 7: Pagination
test_pagination() {
    print_test "Chat History Pagination"
    
    # Create user
    local user=$(random_string)
    local resp=$(curl -s -X POST "$BASE_URL/api/auth/register" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$user\",\"email\":\"${user}@example.com\",\"password\":\"TestPass123\"}")
    
    local token=$(echo "$resp" | jq -r '.data.token')
    local user_id=$(echo "$resp" | jq -r '.data.user.id')
    
    # Test pagination parameters
    local response=$(curl -s -X GET "$BASE_URL/api/messages/history/${user_id}?page=1&per_page=10" \
        -H "Authorization: Bearer $token")
    
    if echo "$response" | jq -e '.data.pagination' > /dev/null 2>&1; then
        print_pass "Pagination parameters accepted"
    else
        print_fail "Pagination test failed: $response"
    fi
}

# Test 8: Invalid User in Chat History
test_invalid_user_chat_history() {
    print_test "Chat History with Invalid User ID"
    
    if [ -z "$TOKEN1" ]; then
        # Create a token for this test
        local user=$(random_string)
        local resp=$(curl -s -X POST "$BASE_URL/api/auth/register" \
            -H "Content-Type: application/json" \
            -d "{\"username\":\"$user\",\"email\":\"${user}@example.com\",\"password\":\"TestPass123\"}")
        TOKEN1=$(echo "$resp" | jq -r '.data.token')
    fi
    
    # Try to get chat history with invalid user ID
    local response=$(curl -s -X GET "$BASE_URL/api/messages/history/999999" \
        -H "Authorization: Bearer $TOKEN1")
    
    if echo "$response" | jq -e '.success == false' > /dev/null 2>&1; then
        print_pass "Invalid user ID correctly rejected"
    else
        print_fail "Invalid user ID should be rejected"
    fi
}

# Print summary
print_summary() {
    echo ""
    echo "======================================"
    echo "          TEST SUMMARY"
    echo "======================================"
    echo "Total Tests:  $TOTAL_TESTS"
    echo -e "Passed:       ${GREEN}$PASSED_TESTS${NC}"
    echo -e "Failed:       ${RED}$FAILED_TESTS${NC}"
    echo "======================================"
    
    if [ $FAILED_TESTS -gt 0 ]; then
        echo ""
        echo "Failed tests:"
        for test_name in "${FAILED_TEST_NAMES[@]}"; do
            echo -e "  ${RED}✗${NC} $test_name"
        done
        echo ""
        exit 1
    else
        echo -e "\n${GREEN}All tests passed!${NC}\n"
        exit 0
    fi
}

# Main test execution
main() {
    echo "======================================"
    echo "    YChat20 API Test Suite"
    echo "======================================"
    echo "Testing server at: $BASE_URL"
    echo ""
    
    check_server
    
    # Run tests
    test_registration
    test_login
    test_get_profile
    test_invalid_login
    test_unauthorized_access
    test_chat_history
    test_pagination
    test_invalid_user_chat_history
    
    # Print summary
    print_summary
}

# Run main
main
