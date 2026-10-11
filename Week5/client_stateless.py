import requests

BASE_URL = "http://127.0.0.1:5000"

access_token = None


# 1. Login
print("--- Login ---")

response = requests.post(f"{BASE_URL}/login", json={
        "username": "alice",
        "password": "password123"
    })

print("Status:", response.status_code)
login_data = response.json()
print(login_data["message"])

access_token = login_data["token"]

print("Token received:", access_token[:30] + "...")


# 2. Request the profile
print("\n--- Profile ---")

headers = {
    "Authorization": f"{access_token}"
}

response = requests.get(
    f"{BASE_URL}/profile",
    headers=headers
)

print("Status:", response.status_code)
print("Response:", response.json())


# 3. Logout
print("\n--- Logout ---")

response = requests.post(
    f"{BASE_URL}/logout",
    headers=headers
)

print("Status:", response.status_code)
print("Response:", response.json())

# Delete the token locally
access_token = None


# 4. Try to access the profile after logout
print("\n--- Profile after logout ---")

if access_token is None:
    print("No token is stored by the client.")
else:
    headers = {
        "Authorization": f"{access_token}"
    }

    response = requests.get(
        f"{BASE_URL}/profile",
        headers=headers
    )

    print("Status:", response.status_code)
    print("Response:", response.json())