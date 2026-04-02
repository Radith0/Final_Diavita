"""Test authentication endpoints."""
import requests
import json

BASE_URL = "http://localhost:5000"


def test_register():
    """Test user registration."""
    print("\n=== Testing User Registration ===")
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "test123",
        "role": "normal"
    }

    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 201


def test_login(username, password):
    """Test user login."""
    print(f"\n=== Testing Login for {username} ===")
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "username": username,
        "password": password
    }

    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")

    if response.status_code == 200:
        return result.get('token')
    return None


def test_get_me(token):
    """Test getting current user info."""
    print("\n=== Testing Get Current User ===")
    url = f"{BASE_URL}/api/auth/me"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_get_all_users(token):
    """Test getting all users (admin only)."""
    print("\n=== Testing Get All Users (Admin Only) ===")
    url = f"{BASE_URL}/api/auth/users"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_my_history(token):
    """Test getting user history."""
    print("\n=== Testing Get My History ===")
    url = f"{BASE_URL}/api/history/my-history"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_my_stats(token):
    """Test getting user statistics."""
    print("\n=== Testing Get My Stats ===")
    url = f"{BASE_URL}/api/history/stats"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_logout(token):
    """Test user logout."""
    print("\n=== Testing Logout ===")
    url = f"{BASE_URL}/api/auth/logout"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def main():
    """Run all tests."""
    print("=" * 50)
    print("Authentication System Test Suite")
    print("=" * 50)

    # Test admin login
    admin_token = test_login("admin", "admin123")

    if admin_token:
        test_get_me(admin_token)
        test_my_history(admin_token)
        test_my_stats(admin_token)
        test_get_all_users(admin_token)

    # Test normal user login
    user_token = test_login("user", "user123")

    if user_token:
        test_get_me(user_token)
        test_my_history(user_token)
        test_my_stats(user_token)

        # Try to access admin endpoint (should fail)
        print("\n=== Testing Admin Access with Normal User (Should Fail) ===")
        test_get_all_users(user_token)

        test_logout(user_token)

    # Test registration (might fail if user already exists)
    # test_register()

    print("\n" + "=" * 50)
    print("Tests Completed!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to the server.")
        print("Make sure the backend is running on http://localhost:5000")
        print("Run: docker-compose up -d")
    except Exception as e:
        print(f"\n❌ Error: {e}")
