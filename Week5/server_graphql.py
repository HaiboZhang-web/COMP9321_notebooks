from flask import Flask, jsonify, request
from ariadne import gql, QueryType, make_executable_schema, graphql_sync


# --------------------------------------
# GraphQL Playground HTML
# --------------------------------------

PLAYGROUND_HTML = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>GraphQL Playground</title>
    <link rel="stylesheet"
      href="//cdn.jsdelivr.net/npm/graphql-playground-react@1.7.20/build/static/css/index.css"/>
    <script src="//cdn.jsdelivr.net/npm/graphql-playground-react@1.7.20/build/static/js/middleware.js"></script>
  </head>
  <body>
    <div id="root"></div>
    <script>
      window.addEventListener("load", function () {
        GraphQLPlayground.init(document.getElementById("root"), {
          endpoint: "/graphql"
        });
      });
    </script>
  </body>
</html>
"""


# --------------------------------------
# GraphQL schema
# --------------------------------------

type_defs = gql(
    """
    type Course {
        code: ID!
        name: String!
    }

    type Student {
        id: ID!
        name: String!
        email: String!
        courses: [Course!]!
    }

    type Query {
        students: [Student!]!
        student(id: ID!): Student
    }
    """
)


# --------------------------------------
# Python classes
# --------------------------------------

class Course:
    def __init__(self, code, name):
        self.code = code
        self.name = name


class Student:
    def __init__(self, student_id, name, email, courses=None):
        self.id = str(student_id)
        self.name = name
        self.email = email
        self.courses = courses or []


# --------------------------------------
# In-memory data
# --------------------------------------

courses_db = {
    "COMP9321": Course(
        "COMP9321",
        "Web Application Engineering"
    ),
    "COMP9417": Course(
        "COMP9417",
        "Machine Learning"
    )
}


students_db = {
    "123": Student(
        student_id="123",
        name="Alice",
        email="alice@example.com",
        courses=[
            courses_db["COMP9321"],
            courses_db["COMP9417"]
        ]
    ),
    "124": Student(
        student_id="124",
        name="Bob",
        email="bob@example.com",
        courses=[
            courses_db["COMP9321"]
        ]
    )
}


# --------------------------------------
# Shared service functions
# --------------------------------------

def get_course(course_code):
    return courses_db.get(course_code)


def get_student(student_id):
    return students_db.get(str(student_id))


def get_all_students():
    return list(students_db.values())


# --------------------------------------
# GraphQL resolvers
# --------------------------------------

query = QueryType()


@query.field("students")
def resolve_students(*_):
    return get_all_students()


@query.field("student")
def resolve_student(*_, id):
    return get_student(id)


# --------------------------------------
# Create executable schema
# --------------------------------------

schema = make_executable_schema(
    type_defs,
    query
)


# --------------------------------------
# Flask application
# --------------------------------------

app = Flask(__name__)


@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or "query" not in data:
        return jsonify({
            "error": "The request body must contain a GraphQL query."
        }), 400

    success, result = graphql_sync(
        schema,
        data,
        context_value={"request": request},
        debug=app.debug
    )

    return jsonify(result), 200 if success else 400


# --------------------------------------
# Run the server
# --------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )