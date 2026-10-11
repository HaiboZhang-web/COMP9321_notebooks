from flask import Flask, session
from flask_restx import Resource, Api

app=Flask(__name__)
api = Api(app)

# Used to sign the session cookie
app.secret_key="my-secret-key"

@app.route("/login")
def login():
    session["username"] ="Alice"
    return "Alice has logged in."

@app.route("/profile")
def profile():
    username = session.get("username")
    if username is None:
        return "Please log in first. ", 401
    
    return f"Welcome, {username}!"

@app.route("/logout")
def logout():
    session.pop("username", None)
    return "You have logged out."

if __name__ =="__main__":
    app.run(debug=True)