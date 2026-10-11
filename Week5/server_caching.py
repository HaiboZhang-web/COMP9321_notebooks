from flask import Flask, request, make_response
import hashlib
import json

app = Flask(__name__)

book = {
    "id": 1,
    "title": "REST Fundamentals"
}


def calculate_etag():
    content = json.dumps(book, sort_keys=True).encode()
    return '"' + hashlib.md5(content).hexdigest() + '"'


@app.route("/books/1", methods=["GET"])
def get_book():
    current_etag = calculate_etag()

    # Read the ETag sent by the client
    client_etag = request.headers.get("If-None-Match")

    # If the cached version is still current
    if client_etag == current_etag:
        response = make_response("", 304)
        response.headers["ETag"] = current_etag

        print("Returned 304 Not Modified")
        return response

    # Otherwise, return the complete resource
    response = make_response(json.dumps(book), 200)
    response.headers["Content-Type"] = "application/json"
    response.headers["Cache-Control"] = "max-age=60"
    response.headers["ETag"] = current_etag

    print("Returned 200 OK with resource")
    return response


@app.route("/books/1/update", methods=["PUT"])
def update_book():
    book["title"] = "Advanced REST Fundamentals"

    return {
        "message": "Book updated",
        "book": book
    }


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)