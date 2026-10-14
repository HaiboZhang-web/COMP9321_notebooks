from flask import Flask, request, jsonify

app = Flask(__name__)

# In a real application, passwords should be hashed and stored in a database.
users = {
    "alice": "password123",
    "bob": "mypassword"
}

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    # Validate username and password
    if username not in users:
        return jsonify({"error": "User does not exist"}), 401

    if users[username] != password:
        return jsonify({"error": "Incorrect password"}), 401

    # Create a simple token after successful validation
    token= f"{username}-token"

    return jsonify({
        "message": "Login successful",
        "token": token
    })


@app.route("/profile", methods=["GET"])
def profile():
    token = request.headers.get("Authorization")
    username = token[:-6]
    # Check that the username exists
    if username not in users:
        return jsonify({"error": "Invalid token"}), 401

    # Authorisation succeeds
    return jsonify({
        "username": username,
        "message": f"Welcome, {username}!"
    })


@app.route("/logout", methods=["POST"])
def logout():
    # The server stores no session.
    # The client should delete its token.
    return jsonify({
        "message": "Logout successful. Delete the token on the client."
    })


if __name__ == "__main__":
    app.run(debug=True)