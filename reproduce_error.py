import requests
import json

url = "http://localhost:8001/api/users/register/"
data = {
    "first_name": "Test",
    "last_name": "User",
    "artist_name": "Test Artist",
    "phone_number": "1234567890",
    "email": "test_error_repro@example.com",
    "password": "password123",
    "confirm_password": "password123",
    "username": "test_error_repro@example.com"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
