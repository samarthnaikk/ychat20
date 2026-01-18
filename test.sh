#!/usr/bin/env bash
# ======================================
# YChat20 API Test Suite (JWT + WAIT FIX)
# ======================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BASE_URL="${BASE_URL:-http://localhost:3000}"
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
FAILED_TEST_NAMES=()

# ---------- helpers ----------

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

random_string() {
  echo "user_$(date +%s)_$RANDOM"
}

auth_header() {
  echo "Authorization: Bearer $1"
}

safe_jq() {
  echo "$1" | jq -r "$2" 2>/dev/null
}

retry_request() {
  local cmd="$1"
  local attempts=2
  local delay=0.3
  local response=""

  for ((i=1;i<=attempts;i++)); do
    response=$(eval "$cmd")
    if echo "$response" | jq -e '.success == true' >/dev/null 2>&1; then
      echo "$response"
      return
    fi
    sleep "$delay"
  done

  echo "$response"
}

# ---------- server check ----------

check_server() {
  print_info "Checking if server is running at $BASE_URL..."
  if ! curl -s "$BASE_URL" >/dev/null; then
    echo -e "${RED}ERROR:${NC} Server not running"
    exit 1
  fi
  print_info "Server is running"
}

# ---------- tests ----------

test_registration() {
  print_test "User Registration"

  USERNAME=$(random_string)
  EMAIL="$USERNAME@test.com"
  PASSWORD="TestPass123"

  RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$USERNAME\",\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

  TOKEN=$(safe_jq "$RESPONSE" '.data.token')
  USER_ID=$(safe_jq "$RESPONSE" '.data.user.id')

  if [ -n "$TOKEN" ]; then
    sleep 0.3
    print_pass "User registration successful (ID: $USER_ID)"
  else
    print_fail "User registration failed: $RESPONSE"
  fi
}

test_login() {
  print_test "User Login"

  RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

  LOGIN_TOKEN=$(safe_jq "$RESPONSE" '.data.token')

  if [ -n "$LOGIN_TOKEN" ]; then
    TOKEN="$LOGIN_TOKEN"
    sleep 0.3
    print_pass "User login successful"
  else
    print_fail "User login failed: $RESPONSE"
  fi
}

test_get_profile() {
  print_test "Get Current User Profile"

  RESPONSE=$(retry_request \
    "curl -s -X GET '$BASE_URL/api/auth/me' -H \"$(auth_header "$TOKEN")\"")

  if echo "$RESPONSE" | jq -e '.success == true' >/dev/null; then
    print_pass "Get profile successful"
  else
    print_fail "Get profile failed: $RESPONSE"
  fi
}

test_invalid_login() {
  print_test "Invalid Login (Wrong Password)"

  RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"invalid@test.com","password":"wrong"}')

  if echo "$RESPONSE" | jq -e '.success == false' >/dev/null; then
    print_pass "Invalid login correctly rejected"
  else
    print_fail "Invalid login should be rejected"
  fi
}

test_unauthorized_access() {
  print_test "Unauthorized Access to Protected Route"

  RESPONSE=$(curl -s "$BASE_URL/api/auth/me")

  if echo "$RESPONSE" | jq -e '.success == false' >/dev/null; then
    print_pass "Unauthorized access correctly denied"
  else
    print_fail "Unauthorized access should be denied"
  fi
}

test_update_profile() {
  print_test "Update Profile - Valid Data"

  NEW_USERNAME="${USERNAME}_updated"

  RESPONSE=$(retry_request \
    "curl -s -X PUT '$BASE_URL/api/auth/profile' \
     -H \"$(auth_header "$TOKEN")\" \
     -H 'Content-Type: application/json' \
     -d '{\"username\":\"$NEW_USERNAME\"}'")

  if echo "$RESPONSE" | jq -e '.success == true' >/dev/null; then
    print_pass "Profile updated successfully"
  else
    print_fail "Profile update failed: $RESPONSE"
  fi
}

test_create_room() {
  print_test "Create Room"

  RESPONSE=$(retry_request \
    "curl -s -X POST '$BASE_URL/api/rooms' \
     -H \"$(auth_header "$TOKEN")\" \
     -H 'Content-Type: application/json' \
     -d '{\"name\":\"Test Room\"}'")

  ROOM_ID=$(safe_jq "$RESPONSE" '.data.room.id')

  if [ -n "$ROOM_ID" ]; then
    print_pass "Room created successfully (ID: $ROOM_ID)"
  else
    print_fail "Room creation failed: $RESPONSE"
  fi
}

test_get_room_messages() {
  print_test "Get Room Messages"

  RESPONSE=$(retry_request \
    "curl -s -X GET '$BASE_URL/api/rooms/$ROOM_ID/messages' \
     -H \"$(auth_header "$TOKEN")\"")

  if echo "$RESPONSE" | jq -e '.success == true' >/dev/null; then
    print_pass "Get room messages successful"
  else
    print_fail "Get room messages failed: $RESPONSE"
  fi
}

# ---------- summary ----------

print_summary() {
  echo ""
  echo "======================================"
  echo "          TEST SUMMARY"
  echo "======================================"
  echo "Total Tests:  $TOTAL_TESTS"
  echo -e "Passed:       ${GREEN}$PASSED_TESTS${NC}"
  echo -e "Failed:       ${RED}$FAILED_TESTS${NC}"
  echo "======================================"

  if [ "$FAILED_TESTS" -gt 0 ]; then
    echo ""
    echo "Failed tests:"
    for t in "${FAILED_TEST_NAMES[@]}"; do
      echo -e "  ${RED}✗${NC} $t"
    done
    exit 1
  else
    echo -e "\n${GREEN}All tests passed!${NC}\n"
    exit 0
  fi
}

# ---------- main ----------

main() {
  echo "======================================"
  echo "    YChat20 API Test Suite"
  echo "======================================"
  echo "Testing server at: $BASE_URL"
  echo ""

  check_server
  test_registration
  test_login
  test_get_profile
  test_invalid_login
  test_unauthorized_access
  test_update_profile
  test_create_room
  test_get_room_messages
  print_summary
}

main
