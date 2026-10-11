import requests

BOOK_URL = "http://127.0.0.1:5000/books/1"
UPDATE_URL = "http://127.0.0.1:5000/books/1/update"

cached_data = None
cached_etag = None


# 1. First request
print("--- First request ---")

response = requests.get(BOOK_URL)

print("Status:", response.status_code)
print("Response:", response.text)

if response.status_code == 200:
    cached_data = response.json()
    cached_etag = response.headers.get("ETag")

print("Cached data:", cached_data)
print("Cached ETag:", cached_etag)


# 2. Second request using the cached ETag
print("\n--- Second request using cache ---")

headers = {
    "If-None-Match": cached_etag
}

response = requests.get(BOOK_URL, headers=headers)

print("Status:", response.status_code)

if response.status_code == 304:
    print("The book has not changed.")
    print("Using cached data:", cached_data)


# 3. Update the book
print("\n--- Updating the book ---")

response = requests.put(UPDATE_URL)

print("Status:", response.status_code)
print("Response:", response.json())


# 4. Request the book again using the old ETag
print("\n--- Request after update ---")

headers = {
    "If-None-Match": cached_etag
}

response = requests.get(BOOK_URL, headers=headers)

print("Status:", response.status_code)

if response.status_code == 304:
    print("The book has not changed.")
    print("Using cached data:", cached_data)

elif response.status_code == 200:
    cached_data = response.json()
    cached_etag = response.headers.get("ETag")

    print("The book has changed.")
    print("New data:", cached_data)
    print("New ETag:", cached_etag)