import requests

URL = "http://127.0.0.1:5000"

#create a client session.
# It automatically stores and resues cookies
client = requests.session()

print("Initial cookies:")
print(client.cookies.get_dict())

#1. Log in
print("\n --- Sending login request ---")

login_response = client.get(f"{URL}/login")

print("status:", login_response.status_code)
print("Headers:", login_response.headers)
print("Set-Cookie:", login_response.headers.get("Set-Cookie"))
print("Response:", login_response.text)
print("Cookies received from server:", client.cookies.get_dict())

# 2. Request the profile
print("\n --- Sending profile request ---")

profile_response = client.get(f"{URL}/profile")

print("status:", profile_response.status_code)
print("Response:", profile_response.text)

print("Cookies sent by the client:")
print(client.cookies.get_dict())

#3. logout first and then request profile
print("\n --- Logout ---")
logout_response = client.get(f"{URL}/logout")
print("status:", logout_response.status_code)
print("Response:", logout_response.text)
print("Cookies sent by the client:")
print(client.cookies.get_dict())

print("\n --- Access profile without log in---")
profile_response = client.get(f"{URL}/profile")

print("status:", profile_response.status_code)
print("Response:", profile_response.text)
