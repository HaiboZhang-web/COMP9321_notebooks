import asyncio

from ariadne import (
    gql,
    make_executable_schema,
    MutationType,
    QueryType,
    SubscriptionType,
)
from ariadne.asgi import GraphQL
from ariadne.asgi.handlers import GraphQLWSHandler
from starlette.responses import HTMLResponse


# --------------------------------------
# GraphQL Playground HTML
# --------------------------------------

PLAYGROUND_HTML = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset=utf-8/>
    <title>GraphQL Playground</title>
    <link rel="stylesheet"
      href="//cdn.jsdelivr.net/npm/graphql-playground-react@1.7.20/build/static/css/index.css"/>
    <link rel="shortcut icon"
      href="//cdn.jsdelivr.net/npm/graphql-playground-react@1.7.20/build/favicon.png"/>
    <script src="//cdn.jsdelivr.net/npm/graphql-playground-react@1.7.20/build/static/js/middleware.js"></script>
    <style>
      .CodeMirror-hint-information {
        display: none !important;
      }
    </style>
  </head>
  <body>
    <div id="root"/>
    <script>
      window.addEventListener('load', function() {
        GraphQLPlayground.init(document.getElementById('root'), {
          endpoint: '/graphql'
        })
      })
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

    type Mutation {
        addStudent(name: String!, email: String!): Student!
    }

    type Subscription {
        studentAdded: Student!
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


# Each active subscription has its own queue. A mutation puts the new student
# into every queue, so every connected subscriber receives the event.
student_subscribers = set()


# --------------------------------------
# Shared service functions
# --------------------------------------

def get_student(student_id):
    return students_db.get(str(student_id))


def get_all_students():
    return list(students_db.values())


# --------------------------------------
# GraphQL resolvers
# --------------------------------------

query = QueryType()
mutation = MutationType()
subscription = SubscriptionType()


@query.field("students")
def resolve_students(*_):
    return get_all_students()


@query.field("student")
def resolve_student(*_, id):
    return get_student(id)


@mutation.field("addStudent")
async def resolve_add_student(*_, name, email):
    """Create an in-memory student and notify active subscribers."""
    if any(student.email.lower() == email.lower()
           for student in students_db.values()):
        raise ValueError(f"A student with email '{email}' already exists.")

    next_id = str(max((int(student_id) for student_id in students_db),
                      default=0) + 1)
    student = Student(student_id=next_id, name=name, email=email)
    students_db[next_id] = student

    # This resolver is async, so queue operations happen on the ASGI event loop.
    for subscriber_queue in tuple(student_subscribers):
        subscriber_queue.put_nowait(student)

    return student


@subscription.source("studentAdded")
async def source_student_added(*_):
    """Yield each student added after this subscription is established."""
    subscriber_queue = asyncio.Queue()
    student_subscribers.add(subscriber_queue)
    try:
        while True:
            yield await subscriber_queue.get()
    finally:
        # Remove disconnected clients to avoid retaining unused queues.
        student_subscribers.discard(subscriber_queue)


@subscription.field("studentAdded")
def resolve_student_added(student, *_):
    """Return the Student yielded by the subscription source."""
    return student


# --------------------------------------
# Create executable schema and ASGI app
# --------------------------------------

schema = make_executable_schema(
    type_defs,
    query,
    mutation,
    subscription
)

# Ariadne's ASGI app handles GraphQL HTTP requests and WebSocket subscriptions.
# GraphQLWSHandler supports the subscriptions-transport-ws protocol used by
# GraphQL Playground-compatible clients.
graphql_app = GraphQL(
    schema,
    websocket_handler=GraphQLWSHandler(),
    debug=True
)


async def app(scope, receive, send):
    """Serve Playground on GET and delegate GraphQL HTTP/WebSocket traffic."""
    if (scope["type"] == "http"
            and scope["path"] == "/graphql"
            and scope["method"] == "GET"):
        response = HTMLResponse(PLAYGROUND_HTML)
        await response(scope, receive, send)
        return

    # Ariadne handles POST requests and WebSocket subscription connections.
    await graphql_app(scope, receive, send)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5000)


# Dependencies:
#   pip install ariadne starlette uvicorn websockets